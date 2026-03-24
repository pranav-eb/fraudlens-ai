import pandas as pd
import numpy as np
from core.ml_model import run_fraud_detection

df = pd.read_csv('temp_export.csv').drop(columns=['fraud_probability'], errors='ignore')
scores = run_fraud_detection(df)["fraud_scores"].values

with open("sweep2.txt", "w") as f:
    for t in np.arange(0.50, 0.96, 0.01):
        f.write(f"{t:.2f}: {int((scores>=t).sum())}\n")
