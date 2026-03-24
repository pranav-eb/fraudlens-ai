import pandas as pd
import numpy as np
from core.ml_model import run_fraud_detection

df_feat = pd.read_csv('temp_export.csv')
if 'fraud_probability' in df_feat.columns:
    df_feat.drop(columns=['fraud_probability'], inplace=True)

results = run_fraud_detection(df_feat)
scores = results["fraud_scores"].values

res = []
for t in np.arange(0.20, 0.70, 0.01):
    res.append(f"{t:.2f}:{int((scores>=t).sum())}")
print(", ".join(res))
