import pandas as pd
import numpy as np
from core.ml_model import run_fraud_detection
import os

try:
    df_feat = pd.read_csv('temp_export.csv')
    df_feat.drop(columns=['fraud_probability'], errors='ignore', inplace=True)
    
    print(f"Loaded user file. Rows: {len(df_feat)}")
    results = run_fraud_detection(df_feat)
    
    # Run a sweep on final_scores
    scores = results["fraud_scores"].values
    
    for t in np.arange(0.20, 0.40, 0.01):
        count = (scores >= t).sum()
        print(f"Threshold {t:.2f} -> {count} frauds")
        
except Exception as e:
    import traceback
    traceback.print_exc()
