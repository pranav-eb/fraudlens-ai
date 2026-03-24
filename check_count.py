import pandas as pd
import os
import sys
import time
sys.path.append(os.getcwd())
from backend.core.ml_model import run_fraud_detection
from backend.core.cleaner import clean_dataframe
from backend.core.features import engineer_features

print("\n🚀 STARTING FAST PERFORMANCE TEST (100k Rows)\n")
start_total = time.time()

# 1. Load
t0 = time.time()
df = pd.read_csv('backend/sample_transactions.csv').head(100000)
print(f"📥 Loaded {len(df)} rows in {time.time()-t0:.2f}s")

# 2. Clean
t0 = time.time()
df_clean, _ = clean_dataframe(df)
print(f"🧹 Cleaned in {time.time()-t0:.2f}s")

# 3. Features
t0 = time.time()
df_features = engineer_features(df_clean)
print(f"🧠 Features engineered in {time.time()-t0:.2f}s")

# 4. Model
t0 = time.time()
results = run_fraud_detection(df_features)
print(f"🤖 ML Inference in {time.time()-t0:.2f}s")

total_time = time.time() - start_total
print(f"\n✅ TOTAL TIME: {total_time:.2f}s")
print(f"FRAUD_COUNT: {len(results['fraud_indices'])}")
