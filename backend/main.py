# backend/main.py
# --------------------------------------------------------------------------
# FraudLens AI – FastAPI Server
# Endpoint: POST /upload
#   Accepts a CSV file, runs the full fraud detection pipeline,
#   and returns a structured JSON response.
# --------------------------------------------------------------------------

import io
import logging
import time

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.cleaner import clean_dataframe
from core.features import engineer_features
from core.ml_model import run_fraud_detection
from core.quality import compute_quality_report

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("fraudlens")

# ── App init ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FraudLens AI",
    description="Explainable Fraud Intelligence Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Helpers ──────────────────────────────────────────────────────────────────

MAX_FILE_SIZE_MB = 200
CHUNK_THRESHOLD  = 50_000    # Read in chunks above this row count

def _read_csv_robust(raw: bytes) -> pd.DataFrame:
    """Try multiple CSV encodings; handle large files gracefully."""
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(io.BytesIO(raw), encoding=enc, low_memory=False)
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"CSV parse error: {e}")
    raise HTTPException(status_code=400, detail="Unable to decode CSV file.")


def _safe_serialize(obj):
    """JSON-safe conversion of numpy/pandas types."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    return obj


def _build_response(df: pd.DataFrame, results: dict, quality_report: dict) -> dict:
    """Construct the final API response from pipeline results."""
    fraud_idx  = results["fraud_indices"]
    scores     = results["fraud_scores"]
    explanations = results["explanations"]
    patterns   = results["patterns"]

    total_txns     = len(df)
    fraud_count    = len(fraud_idx)
    fraud_pct      = round(100 * fraud_count / max(total_txns, 1), 2)

    # ── Top 100 fraud transactions (sorted by score desc) ────────────────
    fraud_df = df.iloc[fraud_idx].copy()
    fraud_df["fraud_score"] = scores.iloc[fraud_idx].values
    fraud_df["explanation"] = [explanations[i] for i in fraud_idx]
    fraud_df = fraud_df.sort_values("fraud_score", ascending=False).head(100)

    top_frauds = []
    for _, row in fraud_df.iterrows():
        top_frauds.append({
            "transaction_id": str(row.get("transaction_id", "")),
            "user_id":        str(row.get("user_id", "")),
            "amount":         _safe_serialize(row.get("transaction_amount", 0)),
            "city":           str(row.get("city", "")),
            "hour":           _safe_serialize(row.get("hour", 0)),
            "fraud_score":    round(float(row["fraud_score"]), 4),
            "reason":         str(row["explanation"]),
        })

    # ── Temporal trend (fraud count by date) ─────────────────────────────
    fraud_by_date: list[dict] = []
    if "timestamp" in df.columns:
        all_df = df.copy()
        all_df["is_fraud_pred"] = 0
        all_df.iloc[fraud_idx, all_df.columns.get_loc("is_fraud_pred")] = 1
        all_df["date_str"] = pd.to_datetime(all_df["timestamp"]).dt.strftime("%Y-%m-%d")
        daily = all_df.groupby("date_str")["is_fraud_pred"].agg(
            total="count", frauds="sum"
        ).reset_index()
        fraud_by_date = daily.rename(columns={"date_str": "date"}).to_dict(orient="records")
        fraud_by_date = [{k: _safe_serialize(v) for k, v in r.items()} for r in fraud_by_date]

    # ── Fraud by city ─────────────────────────────────────────────────────
    fraud_by_city: list[dict] = []
    if "city" in df.columns and fraud_count > 0:
        city_series = fraud_df.groupby("city").size().sort_values(ascending=False).head(10)
        fraud_by_city = [{"city": c, "count": int(v)} for c, v in city_series.items()]

    # ── Top risky users ───────────────────────────────────────────────────
    top_users: list[dict] = []
    if fraud_count > 0 and "user_id" in fraud_df.columns:
        user_risk = (
            fraud_df.groupby("user_id")
            .agg(fraud_txns=("fraud_score", "count"), avg_score=("fraud_score", "mean"))
            .sort_values("fraud_txns", ascending=False)
            .head(10)
            .reset_index()
        )
        top_users = [
            {
                "user_id": str(r["user_id"]),
                "fraud_count": int(r["fraud_txns"]),
                "avg_score": round(float(r["avg_score"]), 4),
            }
            for _, r in user_risk.iterrows()
        ]

    return {
        "total_transactions": total_txns,
        "fraud_count": fraud_count,
        "fraud_percentage": fraud_pct,
        "data_quality_report": quality_report,
        "fraud_patterns": patterns,
        "analytics": {
            "fraud_by_date": fraud_by_date,
            "fraud_by_city": fraud_by_city,
            "top_risky_users": top_users,
        },
        "top_fraud_transactions": top_frauds,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "FraudLens AI"}


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    t0 = time.time()

    # ── File size guard ───────────────────────────────────────────────────
    raw = await file.read()
    size_mb = len(raw) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File too large ({size_mb:.1f} MB). Max {MAX_FILE_SIZE_MB} MB.")

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    logger.info("Received file '%s' (%.2f MB)", file.filename, size_mb)

    # ── Read CSV ──────────────────────────────────────────────────────────
    try:
        df_raw = _read_csv_robust(raw)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

    if len(df_raw) == 0:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty.")

    logger.info("Raw rows: %d, cols: %d", len(df_raw), len(df_raw.columns))

    # ── Phase 1: Clean ────────────────────────────────────────────────────
    try:
        df_clean, cleaning_report = clean_dataframe(df_raw)
    except Exception as e:
        logger.exception("Data cleaning failed")
        raise HTTPException(status_code=500, detail=f"Data cleaning error: {e}")

    # ── Phase 2: Quality report ───────────────────────────────────────────
    quality_report = compute_quality_report(df_clean, cleaning_report)

    # ── Phase 3: Feature engineering ─────────────────────────────────────
    try:
        df_feat = engineer_features(df_clean)
    except Exception as e:
        logger.exception("Feature engineering failed")
        raise HTTPException(status_code=500, detail=f"Feature engineering error: {e}")

    # ── Phase 4: Fraud detection ──────────────────────────────────────────
    try:
        results = run_fraud_detection(df_feat)
    except Exception as e:
        logger.exception("Fraud detection failed")
        raise HTTPException(status_code=500, detail=f"Fraud detection error: {e}")

    # ── Phase 5: Build response ───────────────────────────────────────────
    response = _build_response(df_feat, results, quality_report)

    elapsed = round(time.time() - t0, 2)
    logger.info(
        "Done in %.2fs — %d txns, %d fraud (%.1f%%)",
        elapsed,
        response["total_transactions"],
        response["fraud_count"],
        response["fraud_percentage"],
    )

    return JSONResponse(content=response)
