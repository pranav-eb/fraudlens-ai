import pandas as pd
import json
import traceback
from main import _build_response
from core.cleaner import clean_dataframe
from core.quality import compute_quality_report
from core.features import engineer_features
from core.ml_model import run_fraud_detection

try:
    df = pd.read_csv('sample_transactions.csv')
    df_clean, cleaning_report = clean_dataframe(df)
    quality_report = compute_quality_report(df_clean, cleaning_report)
    df_feat = engineer_features(df_clean)
    results = run_fraud_detection(df_feat)
    
    print('building response')
    response = _build_response(df_feat, results, quality_report)
    
    print('serializing json')
    json.dumps(response)
    print('success')
except Exception as e:
    print("FAILED!")
    traceback.print_exc()
