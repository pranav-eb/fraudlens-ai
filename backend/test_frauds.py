import pandas as pd
import numpy as np

df = pd.read_csv('sample_transactions.csv')
frauds = df[df['is_fraud'] == 1]

print(f"Total frauds: {len(frauds)}")
print("--- Missing Values in Frauds ---")
print(frauds.isna().sum()[frauds.isna().sum() > 0])

print("--- Value Counts for IP ---")
print(frauds['ip_address'].value_counts(dropna=False).head(5))

print("--- City ---")
print(frauds['city'].value_counts(dropna=False).head(5))

print("--- Amounts (Frauds) ---")
print(frauds['transaction_amount'].describe())
print("--- Amounts (All) ---")
print(df['transaction_amount'].describe())
