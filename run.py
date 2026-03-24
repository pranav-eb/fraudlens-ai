import pandas as pd
import numpy as np
import os
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score

def run_simple_pipeline(csv_path="participant_dataset.csv"):
    print(f"\n--- FraudLens AI: Simple End-to-End Pipeline ({csv_path}) ---")
    
    if not os.path.exists(csv_path):
        # Fallback for testing if participant_dataset.csv isn't found
        fallback = "backend/sample_transactions.csv"
        if os.path.exists(fallback):
            print(f"⚠️ {csv_path} not found. Using fallback: {fallback}")
            csv_path = fallback
        else:
            print(f"❌ Error: {csv_path} not found.")
            return

    # 1. LOAD DATA
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} rows.")
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        return

    # 2. MINIMAL CLEANING
    print("🧹 Cleaning data (Minimal & Robust)...")
    
    # Standardize column names (lowercase & underscore)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    
    # Handle amount (Merge transaction_amount and amt)
    if "amt" in df.columns and "transaction_amount" not in df.columns:
        df = df.rename(columns={"amt": "transaction_amount"})
    elif "amt" in df.columns and "transaction_amount" in df.columns:
        df["transaction_amount"] = df["transaction_amount"].fillna(df["amt"])

    # Safely parse transaction_amount
    def safe_amt(val):
        try:
            if pd.isna(val): return 0.0
            s = str(val).replace("₹", "").replace("INR", "").replace("Rs", "").replace(",", "").strip()
            return float(s)
        except: return 0.0

    df["final_amount"] = df.get("transaction_amount", pd.Series([0.0]*len(df))).apply(safe_amt)
    
    # Safely parse timestamp
    ts_col = next((c for c in ["transaction_timestamp", "timestamp", "date", "time"] if c in df.columns), None)
    if ts_col:
        df["timestamp"] = pd.to_datetime(df[ts_col], errors="coerce")
    else:
        df["timestamp"] = pd.Timestamp.now()
    
    # Fill remaining NaNs in timestamp
    df["timestamp"] = df["timestamp"].fillna(pd.Timestamp("2024-01-01"))

    # 3. MINIMAL FEATURES
    print("🧠 Creating behavioral features (Specific subset)...")
    
    # hour
    df["hour"] = df["timestamp"].dt.hour.fillna(0).astype(int)
    
    # is_night (hour < 6 or > 22)
    df["is_night"] = ((df["hour"] < 6) | (df["hour"] > 22)).astype(int)
    
    # location_mismatch (user_location != merchant_location)
    # Handle cases where locations might be missing
    u_loc = df.get("user_location", pd.Series(["unknown"]*len(df))).fillna("unknown").astype(str)
    m_loc = df.get("merchant_location", pd.Series(["unknown"]*len(df))).fillna("unknown").astype(str)
    df["location_mismatch"] = (u_loc != m_loc).astype(int)

    # 4. MODEL TRAINING
    # Prepare features for X
    feature_cols = ["final_amount", "hour", "is_night", "location_mismatch"]
    X = df[feature_cols].fillna(0)
    
    # Target label: find is_fraud or equivalent. If missing, generate pseudo-labels for demo.
    y_col = next((c for c in ["is_fraud", "fraud", "label"] if c in df.columns), None)
    
    if y_col:
        y = pd.to_numeric(df[y_col], errors="coerce").fillna(0).astype(int)
        print(f"📊 Using ground truth labels from '{y_col}'.")
    else:
        print("⚠️ No labels found. Generating pseudo-labels for demonstration purposes...")
        # Simple heuristic for pseudo-labels: High amount + Night + Mismatch
        y = ((df["final_amount"] > df["final_amount"].quantile(0.95)) & 
             ((df["is_night"] == 1) | (df["location_mismatch"] == 1))).astype(int)

    # Train/Test Split logic simplified for hackathon (just train on all and evaluate)
    print("🤖 Training Model (RandomForest with Balanced Weights)...")
    try:
        model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
        model.fit(X, y)
        preds = model.predict(X)
        
        # 5. PRINT RESULTS
        print("\n" + "="*40)
        print("MODEL PERFORMANCE RESULTS")
        print("="*40)
        print(f"Precision: {precision_score(y, preds, zero_division=0):.4f}")
        print(f"Recall:    {recall_score(y, preds, zero_division=0):.4f}")
        print(f"F1 Score:  {f1_score(y, preds, zero_division=0):.4f}")
        print("="*40)
        
        # Simple feature importance
        importances = model.feature_importances_
        print("\nTop Contributing Features:")
        for name, imp in sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True):
            print(f"- {name:20}: {imp:.4f}")
            
    except Exception as e:
        print(f"❌ Model training failed: {e}")

    print("\n✅ Execution Complete.")

if __name__ == "__main__":
    run_simple_pipeline()
