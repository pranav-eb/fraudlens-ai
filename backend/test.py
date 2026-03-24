import pandas as pd
import traceback
from core.cleaner import clean_dataframe
from core.quality import compute_quality_report
from core.features import engineer_features
from core.ml_model import run_fraud_detection

try:
    print('read')
    df = pd.read_csv('sample_transactions.csv')
    print('clean')
    df_clean, cleaning_report = clean_dataframe(df)
    print('feat')
    df_feat = engineer_features(df_clean)
    print('quality')
    compute_quality_report(df_clean, cleaning_report)
    print('ml')
    run_fraud_detection(df_feat)
    print('success')
except Exception as e:
    traceback.print_exc()
