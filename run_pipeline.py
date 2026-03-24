import pandas as pd
import numpy as np
import os
import sys

# Ensure backend modules are importable
sys.path.append(os.path.join(os.getcwd(), "backend"))

from core.cleaner import clean_dataframe, generate_quality_report
from core.features import engineer_features
from core.ml_model import run_fraud_detection, explain_prediction

def run_pipeline(csv_path="backend/sample_transactions.csv"):
    print("\n🚀 FRAUDLENS AI: HACKATHON PIPELINE STARTING\n")
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found.")
        return

    # 1. Load Data
    print(f"📥 Loading dataset: {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # 2. Clean Data & Generate Quality Report
    print("🧹 Cleaning data and validating quality flags...")
    df_clean, cleaning_meta = clean_dataframe(df)
    quality_report = generate_quality_report(df_clean)
    
    # 3. Feature Engineering
    print("🧠 Engineering behavioral features...")
    df_features = engineer_features(df_clean)
    
    # 4. Model Training & Evaluation
    print("🤖 Running dual-engine (Isolation Forest + Random Forest) detection...")
    results = run_fraud_detection(df_features)
    
    # 5. Explainability Demo
    print("🔍 EXPLAINABILITY DEMO (Sampling Detected Frauds):")
    fraud_indices = results["fraud_indices"]
    if fraud_indices:
        print(f"Found {len(fraud_indices)} suspicious transactions.")
        # Explain top 3
        for idx in fraud_indices[:3]:
            row = df_features.iloc[idx]
            explanation = explain_prediction(row)
            print(f"  - TXN {row['transaction_id']}: {explanation}")
    else:
        print("  - No frauds detected in this sample.")
        
    print("\n✅ PIPELINE EXECUTION COMPLETE")

if __name__ == "__main__":
    # If a path is provided as an argument, use it
    target_csv = sys.argv[1] if len(sys.argv) > 1 else "backend/sample_transactions.csv"
    run_pipeline(target_csv)
