# backend/core/ml_model.py
# --------------------------------------------------------------------------
# Hybrid Fraud Detection Engine
# Combines:
#   1. Isolation Forest (anomaly score)
#   2. RandomForest (fraud probability via pseudo-labels)
#   3. Rule-based scoring
# Final score = weighted blend → classify as fraud if > threshold
# Also runs KMeans fraud pattern clustering and generates logic explanations.
# --------------------------------------------------------------------------

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans, DBSCAN
import logging

from .features import ML_FEATURES

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────
ISOLATION_WEIGHT   = 0.30
RF_WEIGHT          = 0.40
RULE_WEIGHT        = 0.30
FRAUD_THRESHOLD    = 0.50   # Final combined score ≥ this → fraud
N_FRAUD_CLUSTERS   = 5      # KMeans target clusters for fraud patterns

# Named fraud patterns (matched by cluster centroid dominant feature)
PATTERN_DEFINITIONS = [
    {
        "name": "High-Value Spike Fraud",
        "description": "Unusually large transaction far exceeding the user's historical average.",
        "key_feature": "amount_ratio",
    },
    {
        "name": "Rapid Micro-Transaction Fraud",
        "description": "Multiple small transactions executed at high velocity within a short time window.",
        "key_feature": "velocity_score",
    },
    {
        "name": "New Device Fraud",
        "description": "Transaction initiated from a device never previously associated with the account.",
        "key_feature": "is_new_device",
    },
    {
        "name": "Location Anomaly Fraud",
        "description": "Transaction from a city or region outside the user's known geographic activity.",
        "key_feature": "is_new_location",
    },
    {
        "name": "Shared Device Fraud",
        "description": "Transaction from a device shared across multiple user accounts — indicative of account takeover or synthetic identity fraud.",
        "key_feature": "cross_user_device",
    },
]


def _safe_feature_matrix(df: pd.DataFrame) -> np.ndarray:
    """Extract and sanitize the feature matrix to avoid NaN/Inf issues."""
    available = [f for f in ML_FEATURES if f in df.columns]
    X = df[available].copy()
    # Fill remaining NaN with column median, then 0
    X = X.fillna(X.median(numeric_only=True)).fillna(0.0)
    X = X.replace([np.inf, -np.inf], 0.0)
    return X.values.astype(np.float64), available


def _compute_rule_score(row: pd.Series) -> float:
    """
    Rule-based fraud score for a single transaction row.
    Returns a value in [0, 1].
    """
    score = 0.0
    reasons = []

    # Rule 1: Amount > 5x user average
    if row.get("amount_ratio", 1.0) >= 5.0:
        score += 0.35
        reasons.append(f"amount is {row['amount_ratio']:.1f}x higher than user average")

    # Rule 2: New device + new location simultaneously
    if row.get("is_new_device", 0) and row.get("is_new_location", 0):
        score += 0.30
        reasons.append("new device AND new location")

    # Rule 3: High velocity (> 5 txns/hour)
    v = row.get("velocity_score", 1)
    if v > 5:
        score += min(0.25, 0.05 * (v - 5))
        reasons.append(f"{v} transactions in the same hour")

    # Rule 4: Unusual time (0–5 AM)
    h = row.get("hour", 12)
    if 0 <= h <= 5:
        score += 0.15
        reasons.append(f"transaction at {h}:00 AM (unusual hour)")

    # Rule 5: Cross-user device
    if row.get("cross_user_device", 0):
        score += 0.25
        reasons.append("device shared with other user accounts")

    # Rule 6: New device alone
    if row.get("is_new_device", 0) and not row.get("is_new_location", 0):
        score += 0.10
        reasons.append("new device not seen before")

    # Rule 7: New location alone
    if row.get("is_new_location", 0) and not row.get("is_new_device", 0):
        score += 0.10
        reasons.append("new location not seen before")

    # Rule 8: Invalid IP
    if row.get("ip_valid", 1) == 0:
        score += 0.10
        reasons.append("invalid or suspicious IP address")

    # Rule 9: High balance deviation
    if abs(row.get("balance_deviation", 0.0)) > 3.0:
        score += 0.10
        reasons.append("significant balance anomaly")

    return min(1.0, score), reasons


def _build_explanation(row: pd.Series, reasons: list[str]) -> str:
    """Generate a human-readable explanation string for a flagged transaction."""
    if not reasons:
        return "Transaction flagged due to combined anomaly signals across multiple features."

    base = "This transaction is suspicious because"
    parts = []
    for i, r in enumerate(reasons[:4]):  # cap at 4 reasons for readability
        if i == 0:
            parts.append(f" it has {r}")
        else:
            parts.append(f" {r}")

    explanation = base + "," + ",".join(parts) + "."
    return explanation.replace(",,", ",").replace(" .", ".")


def run_fraud_detection(df: pd.DataFrame) -> dict:
    """
    Main entry point. Runs the full hybrid pipeline and returns:
    {
        fraud_indices:   list[int]          # row indices flagged as fraud
        fraud_scores:    pd.Series          # final combined score per row
        explanations:    list[str]          # per-row explanation string
        rule_reasons:    list[list[str]]    # raw rule reasons
        patterns:        list[dict]         # cluster pattern summaries
    }
    """
    n = len(df)
    if n == 0:
        return {
            "fraud_indices": [], "fraud_scores": pd.Series(dtype=float),
            "explanations": [], "rule_reasons": [], "patterns": []
        }

    X, used_features = _safe_feature_matrix(df)

    # ── 1. Isolation Forest (anomaly detection) ─────────────────────────────
    logger.info("Running Isolation Forest on %d rows …", n)
    contamination = min(0.15, max(0.01, 500 / n))  # adaptive contamination
    iso = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    iso.fit(X)
    raw_scores = iso.score_samples(X)            # more negative → more anomalous
    # Normalise to [0,1] where 1 = most anomalous
    iso_scores = 1 - MinMaxScaler().fit_transform(raw_scores.reshape(-1, 1)).flatten()
    iso_pseudo_labels = (iso.predict(X) == -1).astype(int)   # 1=anomaly

    # ── 2. Rule-based scoring ────────────────────────────────────────────────
    logger.info("Computing rule-based scores …")
    rule_scores_list = []
    rule_reasons_list = []
    for _, row in df.iterrows():
        s, r = _compute_rule_score(row)
        rule_scores_list.append(s)
        rule_reasons_list.append(r)
    rule_scores = np.array(rule_scores_list)

    # ── 3. Pseudo-label generation for RandomForest ─────────────────────────
    # Combine iso anomaly + rule score to generate pseudo-labels for the RF
    pseudo_score = 0.5 * iso_scores + 0.5 * rule_scores
    pseudo_labels = (pseudo_score >= 0.45).astype(int)

    fraud_count_pseudo = pseudo_labels.sum()
    non_fraud_count_pseudo = n - fraud_count_pseudo

    logger.info("Pseudo-labels: %d fraud / %d non-fraud", fraud_count_pseudo, non_fraud_count_pseudo)

    # ── 4. RandomForest classification ──────────────────────────────────────
    rf_proba = np.zeros(n, dtype=float)
    if fraud_count_pseudo >= 5 and non_fraud_count_pseudo >= 5:
        logger.info("Training RandomForest …")
        # Class weights to handle imbalance
        rf = RandomForestClassifier(
            n_estimators=150,
            max_depth=8,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        rf.fit(X, pseudo_labels)
        rf_proba = rf.predict_proba(X)[:, 1]
    else:
        # Fall back to iso_scores if too few samples in one class
        rf_proba = iso_scores.copy()

    # ── 5. Final combined score ──────────────────────────────────────────────
    final_scores = (
        ISOLATION_WEIGHT * iso_scores +
        RF_WEIGHT        * rf_proba   +
        RULE_WEIGHT      * rule_scores
    )
    final_scores = np.clip(final_scores, 0.0, 1.0)

    is_fraud = final_scores >= FRAUD_THRESHOLD
    fraud_indices = list(np.where(is_fraud)[0])

    # ── 6. Generate explanations ─────────────────────────────────────────────
    explanations = []
    for i, (_, row) in enumerate(df.iterrows()):
        if is_fraud[i]:
            explanations.append(_build_explanation(row, rule_reasons_list[i]))
        else:
            explanations.append("")

    # ── 7. Fraud pattern clustering ──────────────────────────────────────────
    patterns = []
    if len(fraud_indices) >= N_FRAUD_CLUSTERS:
        patterns = _cluster_fraud_patterns(df, fraud_indices, used_features)
    elif len(fraud_indices) > 0:
        patterns = _cluster_fraud_patterns(df, fraud_indices, used_features,
                                           n_clusters=max(1, len(fraud_indices) // 2))

    return {
        "fraud_indices":   fraud_indices,
        "fraud_scores":    pd.Series(final_scores, index=df.index),
        "explanations":    explanations,
        "rule_reasons":    rule_reasons_list,
        "patterns":        patterns,
    }


def _cluster_fraud_patterns(df: pd.DataFrame, fraud_indices: list[int],
                             used_features: list[str], n_clusters: int = N_FRAUD_CLUSTERS) -> list[dict]:
    """
    Cluster fraudulent transactions with KMeans.
    Each cluster is labelled by its dominant feature using PATTERN_DEFINITIONS.
    """
    fraud_df = df.iloc[fraud_indices].copy()
    pattern_features = [f for f in [
        "amount_ratio", "velocity_score", "is_new_device",
        "is_new_location", "cross_user_device",
    ] if f in fraud_df.columns]

    if len(pattern_features) == 0 or len(fraud_df) < 2:
        return []

    X_fraud = fraud_df[pattern_features].fillna(0).values.astype(float)
    X_scaled = MinMaxScaler().fit_transform(X_fraud)

    n_clusters = min(n_clusters, len(fraud_df))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    fraud_df = fraud_df.copy()
    fraud_df["cluster"] = labels

    patterns_out = []
    used_pattern_names = set()

    for c in range(n_clusters):
        cluster_mask = labels == c
        cluster_size = int(cluster_mask.sum())
        if cluster_size == 0:
            continue

        centroid = kmeans.cluster_centers_[c]
        # Find the dominant feature in this cluster's centroid
        dominant_feat_idx = int(np.argmax(centroid))
        dominant_feat = pattern_features[dominant_feat_idx]

        # Match to a named pattern
        matched = None
        for pdef in PATTERN_DEFINITIONS:
            if pdef["key_feature"] == dominant_feat and pdef["name"] not in used_pattern_names:
                matched = pdef
                break
        if matched is None:
            matched = {
                "name": f"Mixed Anomaly Pattern {c+1}",
                "description": f"Cluster of {cluster_size} transactions with combined anomaly signals.",
                "key_feature": dominant_feat,
            }

        used_pattern_names.add(matched["name"])
        patterns_out.append({
            "pattern_name":  matched["name"],
            "count":         cluster_size,
            "description":   matched["description"],
            "dominant_feature": dominant_feat,
        })

    # Sort by count descending
    patterns_out.sort(key=lambda x: x["count"], reverse=True)
    return patterns_out
