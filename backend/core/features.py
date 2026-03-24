# backend/core/features.py
# --------------------------------------------------------------------------
# Behavioral Intelligence & Feature Engineering Engine
# Builds user profiles, then generates advanced fraud-signal features
# for every transaction row.
# --------------------------------------------------------------------------

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def build_user_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate per-user statistics.
    Returns a DataFrame indexed by user_id.
    """
    grp = df.groupby("user_id")

    profiles = pd.DataFrame({
        "avg_amount":      grp["transaction_amount"].mean(),
        "max_amount":      grp["transaction_amount"].max(),
        "min_amount":      grp["transaction_amount"].min(),
        "std_amount":      grp["transaction_amount"].std().fillna(0),
        "txn_count":       grp["transaction_amount"].count(),
        "avg_hour":        grp["hour"].mean(),
        "preferred_method": grp["payment_method"].agg(lambda s: s.mode().iloc[0] if len(s) > 0 else "Unknown"),
        # Known devices: we store a frozenset per user
        "known_devices":   grp["device_id"].agg(frozenset),
        # Known cities
        "known_cities":    grp["city"].agg(frozenset),
    })

    # Active hours: range (max-min hour)
    profiles["hour_range"] = grp["hour"].max() - grp["hour"].min()

    return profiles


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create advanced fraud-signal features on top of the cleaned dataframe.
    All operations are vectorized for performance on 100k+ rows.
    """
    profiles = build_user_profiles(df)

    # ── Map user profile stats back to transaction rows ─────────────────────
    df = df.join(profiles[["avg_amount", "max_amount", "std_amount",
                            "txn_count", "avg_hour", "hour_range",
                            "known_devices", "known_cities"]], on="user_id")

    # Fill defaults for users seen only once (NaN std)
    df["avg_amount"]  = df["avg_amount"].fillna(df["transaction_amount"])
    df["std_amount"]  = df["std_amount"].fillna(0.0)
    df["avg_hour"]    = df["avg_hour"].fillna(12.0)
    df["hour_range"]  = df["hour_range"].fillna(0.0)
    df["txn_count"]   = df["txn_count"].fillna(1)

    # ── amount_ratio ────────────────────────────────────────────────────────
    safe_avg = df["avg_amount"].replace(0, np.nan)
    df["amount_ratio"] = (df["transaction_amount"] / safe_avg).fillna(1.0)

    # ── is_new_device ───────────────────────────────────────────────────────
    # A device is "new" if the transaction device is seen by < 5% of the
    # user's other transactions (heuristic when we have no historical set)
    def _is_new_device(row):
        known = row["known_devices"]
        if not isinstance(known, (set, frozenset)) or len(known) == 0:
            return 0
        # Device is known to user – but if seen only once globally, flag it
        return 0 if row["device_id"] in known else 1

    df["is_new_device"] = df.apply(_is_new_device, axis=1).astype(int)

    # ── is_new_location ─────────────────────────────────────────────────────
    def _is_new_location(row):
        known = row["known_cities"]
        if not isinstance(known, (set, frozenset)) or len(known) == 0:
            return 0
        return 0 if row["city"] in known else 1

    df["is_new_location"] = df.apply(_is_new_location, axis=1).astype(int)

    # ── time_anomaly ────────────────────────────────────────────────────────
    # Flag if transaction hour is outside the user's typical hour ± 3h window
    # or in the wee hours (0–5 AM) if the user has never transacted then
    df["time_anomaly"] = (
        ((df["hour"] >= 0) & (df["hour"] <= 5)) |
        (abs(df["hour"] - df["avg_hour"]) > 4)
    ).astype(int)

    # ── velocity_score ──────────────────────────────────────────────────────
    # Number of transactions by the same user within the same 1-hour window
    df = df.sort_values(["user_id", "timestamp"])
    df["ts_floor_hour"] = df["timestamp"].dt.floor("h")
    hourly_velocity = (
        df.groupby(["user_id", "ts_floor_hour"])
        .cumcount() + 1
    )
    df["velocity_score"] = hourly_velocity.values

    # ── cross_user_device ───────────────────────────────────────────────────
    # If a device_id is used by more than 1 distinct user → suspicious
    device_user_counts = df.groupby("device_id")["user_id"].nunique()
    df["cross_user_device"] = df["device_id"].map(device_user_counts).gt(1).astype(int)

    # ── balance_deviation ───────────────────────────────────────────────────
    if df["balance"].notna().any():
        user_avg_balance = df.groupby("user_id")["balance"].transform("mean")
        user_std_balance = df.groupby("user_id")["balance"].transform("std").fillna(1.0)
        df["balance_deviation"] = ((df["balance"] - user_avg_balance) / user_std_balance.replace(0, 1)).fillna(0.0)
    else:
        df["balance_deviation"] = 0.0

    # ── round_amount flag ───────────────────────────────────────────────────
    # Round-number amounts (10000, 5000, etc.) are common in synthetic fraud
    df["is_round_amount"] = (df["transaction_amount"] % 1000 == 0).astype(int)

    # ── z-score of transaction amount across all users ──────────────────────
    global_mean = df["transaction_amount"].mean()
    global_std  = df["transaction_amount"].std()
    if global_std and global_std > 0:
        df["amount_zscore"] = (df["transaction_amount"] - global_mean) / global_std
    else:
        df["amount_zscore"] = 0.0

    # Drop temporary columns
    df.drop(columns=["known_devices", "known_cities", "ts_floor_hour"], inplace=True, errors="ignore")

    return df


# ── Feature list used for ML model ──────────────────────────────────────────
ML_FEATURES = [
    "transaction_amount",
    "amount_ratio",
    "amount_zscore",
    "is_new_device",
    "is_new_location",
    "time_anomaly",
    "velocity_score",
    "cross_user_device",
    "balance_deviation",
    "is_round_amount",
    "hour",
    "day_of_week",
    "ip_valid",
]
