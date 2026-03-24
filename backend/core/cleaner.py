# backend/core/cleaner.py
# --------------------------------------------------------------------------
# Data Cleaning Engine
# Handles: currency parsing, timestamp normalization, city name normalization,
#          IP validation, duplicate removal, missing value handling
# --------------------------------------------------------------------------

import re
import pandas as pd
import numpy as np
from dateutil import parser as dateutil_parser
import logging

logger = logging.getLogger(__name__)

# ── City alias map ──────────────────────────────────────────────────────────
CITY_ALIASES: dict[str, str] = {
    "bom": "Mumbai", "bombay": "Mumbai", "mumbai": "Mumbai",
    "del": "Delhi", "new delhi": "Delhi", "delhi": "Delhi", "ndls": "Delhi",
    "blr": "Bangalore", "bengaluru": "Bangalore", "bangalore": "Bangalore",
    "ccu": "Kolkata", "calcutta": "Kolkata", "kolkata": "Kolkata",
    "maa": "Chennai", "madras": "Chennai", "chennai": "Chennai",
    "hyd": "Hyderabad", "hyderabad": "Hyderabad",
    "pnq": "Pune", "pune": "Pune",
    "amd": "Ahmedabad", "ahmedabad": "Ahmedabad",
    "jai": "Jaipur", "jaipur": "Jaipur",
    "lko": "Lucknow", "lucknow": "Lucknow",
    "surat": "Surat",
}

# ── IP validation regex ─────────────────────────────────────────────────────
_IP_RE = re.compile(
    r"^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$"
)


def _parse_amount(val) -> float | None:
    """Convert currency strings like '₹1,23,456.78' or 'INR 900' to float."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    # Remove ₹, INR, commas, spaces
    s = re.sub(r"[₹,\s]", "", s, flags=re.IGNORECASE)
    s = re.sub(r"(?i)inr", "", s)
    try:
        return float(s)
    except ValueError:
        return None


def _parse_timestamp(val) -> pd.Timestamp | None:
    """Attempt to parse any datetime-like string."""
    if pd.isna(val):
        return None
    try:
        return pd.Timestamp(dateutil_parser.parse(str(val)))
    except Exception:
        return None


def _normalize_city(val) -> str:
    """Normalize city name using alias map."""
    if pd.isna(val):
        return "Unknown"
    return CITY_ALIASES.get(str(val).strip().lower(), str(val).strip().title())


def _is_valid_ip(val) -> bool:
    """Return True if val is a valid IPv4 address."""
    if pd.isna(val):
        return False
    return bool(_IP_RE.match(str(val).strip()))


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Main cleaning pipeline. Returns (cleaned_df, cleaning_report).
    
    Handles all messy real-world scenarios without blindly dropping rows.
    """
    report: dict = {}
    original_rows = len(df)

    # ── 1. Lowercase column names ───────────────────────────────────────────
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # ── 2. Merge 'amt' → 'transaction_amount' ──────────────────────────────
    if "amt" in df.columns and "transaction_amount" not in df.columns:
        df = df.rename(columns={"amt": "transaction_amount"})
    elif "amt" in df.columns and "transaction_amount" in df.columns:
        # Fill gaps
        mask = df["transaction_amount"].isna()
        df.loc[mask, "transaction_amount"] = df.loc[mask, "amt"]
        df.drop(columns=["amt"], inplace=True)

    # ── 3. Parse transaction_amount ─────────────────────────────────────────
    if "transaction_amount" in df.columns:
        df["transaction_amount"] = df["transaction_amount"].apply(_parse_amount)
        # Impute with median; flag rows with originally missing amount
        median_amt = df["transaction_amount"].median()
        if pd.isna(median_amt):
            median_amt = 0.0
        df["amount_imputed"] = df["transaction_amount"].isna().astype(int)
        df["transaction_amount"] = df["transaction_amount"].fillna(median_amt)
    else:
        df["transaction_amount"] = 0.0
        df["amount_imputed"] = 0

    # ── 4. Normalize timestamps ─────────────────────────────────────────────
    ts_col = next((c for c in ["timestamp", "transaction_time", "date", "txn_time"] if c in df.columns), None)
    if ts_col:
        df["timestamp"] = df[ts_col].apply(_parse_timestamp)
        if ts_col != "timestamp":
            df.drop(columns=[ts_col], inplace=True)
        # Rows with unparseable timestamps: use median epoch
        nat_mask = df["timestamp"].isna()
        report["unparseable_timestamps"] = int(nat_mask.sum())
        if nat_mask.any():
            median_ts = df["timestamp"].dropna().sort_values().iloc[len(df["timestamp"].dropna()) // 2] if df["timestamp"].notna().any() else pd.Timestamp("2024-01-01")
            df.loc[nat_mask, "timestamp"] = median_ts
        df["hour"] = df["timestamp"].dt.hour.fillna(12).astype(int)
        df["day_of_week"] = df["timestamp"].dt.dayofweek.fillna(0).astype(int)
    else:
        df["timestamp"] = pd.Timestamp("2024-01-01")
        df["hour"] = 12
        df["day_of_week"] = 0

    # ── 5. Normalize city names ─────────────────────────────────────────────
    city_col = next((c for c in ["city", "location", "merchant_city"] if c in df.columns), None)
    if city_col:
        df["city"] = df[city_col].apply(_normalize_city)
        if city_col != "city":
            df.drop(columns=[city_col], inplace=True)
    else:
        df["city"] = "Unknown"

    # ── 6. Standardize user_id column ──────────────────────────────────────
    uid_col = next((c for c in ["user_id", "customer_id", "account_id", "uid"] if c in df.columns), None)
    if uid_col:
        if uid_col != "user_id":
            df = df.rename(columns={uid_col: "user_id"})
        df["user_id"] = df["user_id"].astype(str).str.strip()
    else:
        df["user_id"] = "UNKNOWN"

    # ── 7. Standardize transaction_id ──────────────────────────────────────
    txn_col = next((c for c in ["transaction_id", "txn_id", "trans_id", "id"] if c in df.columns), None)
    if txn_col:
        if txn_col != "transaction_id":
            df = df.rename(columns={txn_col: "transaction_id"})
        df["transaction_id"] = df["transaction_id"].astype(str).str.strip()
    else:
        df["transaction_id"] = [f"TXN{i:08d}" for i in range(len(df))]

    # ── 8. Validate IP addresses ────────────────────────────────────────────
    ip_col = next((c for c in ["ip", "ip_address", "ip_addr"] if c in df.columns), None)
    if ip_col:
        df["ip_address"] = df[ip_col].astype(str)
        if ip_col != "ip_address":
            df.drop(columns=[ip_col], inplace=True)
        df["ip_valid"] = df["ip_address"].apply(_is_valid_ip).astype(int)
        report["invalid_ips"] = int((df["ip_valid"] == 0).sum())
    else:
        df["ip_address"] = "0.0.0.0"
        df["ip_valid"] = 0
        report["invalid_ips"] = 0

    # ── 9. Device & payment method normalization ────────────────────────────
    dev_col = next((c for c in ["device_id", "device", "device_type"] if c in df.columns), None)
    if dev_col:
        if dev_col != "device_id":
            df = df.rename(columns={dev_col: "device_id"})
        df["device_id"] = df["device_id"].astype(str).str.strip().fillna("UNKNOWN")
    else:
        df["device_id"] = "UNKNOWN"

    pay_col = next((c for c in ["payment_method", "payment_type", "method"] if c in df.columns), None)
    if pay_col:
        if pay_col != "payment_method":
            df = df.rename(columns={pay_col: "payment_method"})
        df["payment_method"] = df["payment_method"].astype(str).str.strip().str.title().fillna("Unknown")
    else:
        df["payment_method"] = "Unknown"

    # ── 10. Handle is_fraud label (optional ground truth) ──────────────────
    fraud_col = next((c for c in ["is_fraud", "fraud", "fraud_flag", "label"] if c in df.columns), None)
    if fraud_col:
        df["is_fraud_label"] = pd.to_numeric(df[fraud_col], errors="coerce").fillna(0).astype(int)
        report["has_ground_truth"] = True
    else:
        df["is_fraud_label"] = -1  # Sentinel → no labels
        report["has_ground_truth"] = False

    # ── 11. Remove exact duplicate rows ────────────────────────────────────
    dup_rows = int(df.duplicated().sum())
    df = df.drop_duplicates()
    report["duplicate_rows_removed"] = dup_rows

    # ── 12. Remove duplicate transaction_ids (keep first) ──────────────────
    dup_txn = int(df.duplicated(subset=["transaction_id"]).sum())
    df = df.drop_duplicates(subset=["transaction_id"], keep="first")
    report["duplicate_txn_ids_removed"] = dup_txn

    # ── 13. Ensure numeric types ────────────────────────────────────────────
    df["transaction_amount"] = pd.to_numeric(df["transaction_amount"], errors="coerce").fillna(0.0)

    # ── 14. Balance column ──────────────────────────────────────────────────
    bal_col = next((c for c in ["balance", "account_balance", "avail_balance"] if c in df.columns), None)
    if bal_col:
        df["balance"] = pd.to_numeric(df[bal_col], errors="coerce")
        if bal_col != "balance":
            df.drop(columns=[bal_col], inplace=True)
        bal_median = df["balance"].median()
        df["balance"] = df["balance"].fillna(bal_median if not pd.isna(bal_median) else 0.0)
    else:
        df["balance"] = np.nan  # Will be handled downstream

    report["original_rows"] = original_rows
    report["clean_rows"] = len(df)
    return df.reset_index(drop=True), report
