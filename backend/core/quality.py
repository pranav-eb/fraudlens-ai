# backend/core/quality.py
# --------------------------------------------------------------------------
# Data Quality Reporting Module
# Produces a 0-100 quality score and structured column-level diagnostics.
# --------------------------------------------------------------------------

import pandas as pd
import numpy as np


def compute_quality_report(df: pd.DataFrame, cleaning_report: dict) -> dict:
    """
    Given a cleaned DataFrame and the cleaning_report from cleaner.py,
    produce a detailed quality report with a composite quality score.
    """
    total_rows = max(cleaning_report.get("original_rows", len(df)), 1)
    clean_rows = len(df)
    total_cells = len(df) * len(df.columns)

    # ── Per-column missing value counts ────────────────────────────────────
    missing_per_col: dict[str, int] = {}
    for col in df.columns:
        mc = int(df[col].isna().sum())
        if mc > 0:
            missing_per_col[col] = mc

    total_missing = sum(missing_per_col.values())
    missing_pct = round(100 * total_missing / max(total_cells, 1), 2)

    # ── Duplicate metrics ───────────────────────────────────────────────────
    dup_rows = cleaning_report.get("duplicate_rows_removed", 0)
    dup_txns = cleaning_report.get("duplicate_txn_ids_removed", 0)
    dup_pct = round(100 * dup_rows / total_rows, 2)

    # ── Invalid IP count ────────────────────────────────────────────────────
    invalid_ips = cleaning_report.get("invalid_ips", 0)
    ip_valid_pct = round(100 * (1 - invalid_ips / max(clean_rows, 1)), 2)

    # ── Amount imputation ───────────────────────────────────────────────────
    imputed_amounts = int(df.get("amount_imputed", pd.Series([0])).sum())

    # ── Unparseable timestamps ──────────────────────────────────────────────
    bad_timestamps = cleaning_report.get("unparseable_timestamps", 0)

    # ── Composite Quality Score (0–100) ─────────────────────────────────────
    # Penalise:
    #   - missing values   → up to -25 pts
    #   - duplicate rows   → up to -20 pts
    #   - duplicate txn    → up to -20 pts
    #   - invalid IPs      → up to -15 pts
    #   - bad timestamps   → up to -10 pts
    #   - imputed amounts  → up to -10 pts

    score = 100.0
    score -= min(25, missing_pct * 0.5)
    score -= min(20, dup_pct * 0.4)
    score -= min(20, 100 * dup_txns / max(total_rows, 1) * 0.4)
    score -= min(15, (100 - ip_valid_pct) * 0.15)
    score -= min(10, 100 * bad_timestamps / max(total_rows, 1) * 0.1)
    score -= min(10, 100 * imputed_amounts / max(total_rows, 1) * 0.1)
    score = max(0.0, round(score, 1))

    report = {
        "quality_score": score,
        "total_rows_original": total_rows,
        "clean_rows": clean_rows,
        "total_columns": len(df.columns),
        "missing_values": {
            "total_missing": total_missing,
            "missing_pct": missing_pct,
            "per_column": missing_per_col,
        },
        "duplicates": {
            "duplicate_rows_removed": dup_rows,
            "duplicate_txn_ids_removed": dup_txns,
            "duplicate_row_pct": dup_pct,
        },
        "ip_quality": {
            "invalid_ip_count": invalid_ips,
            "valid_ip_pct": ip_valid_pct,
        },
        "timestamp_issues": bad_timestamps,
        "amount_imputed_count": imputed_amounts,
        "has_ground_truth_labels": cleaning_report.get("has_ground_truth", False),
    }
    return report
