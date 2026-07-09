import pandas as pd
import joblib


users  = pd.read_csv('users.csv')
logs   = pd.read_csv('InteractiveSignIns.csv')
merged = pd.merge(logs, users, left_on='User ID', right_on='id', how='inner').reset_index(drop=True)


model = joblib.load('isolation_forest_model.pkl')
ml = pd.read_csv('ml_ready_logs.csv').reindex(columns=model.feature_names_in_, fill_value=0)
scores = model.decision_function(ml)
preds = model.predict(ml)
ml['anomaly_score'] = scores
ml['risk_flag']     = (preds == -1)


identity_cols = ['displayName', 'userPrincipalName', 'Date (UTC)', 'Location',
                 'IP address', 'Browser', 'Operating System', 'Application', 'Status']
identity_cols = [c for c in identity_cols if c in merged.columns]

enriched = merged[identity_cols].copy()
enriched['anomaly_score'] = ml['anomaly_score'].values
enriched['risk_flag']     = ml['risk_flag'].values


top = enriched[enriched['risk_flag']].sort_values('anomaly_score').head(10)
top.to_csv('top_anomalies_named.csv', index=False)
print(top[['displayName', 'Date (UTC)', 'Location', 'anomaly_score']].to_string(index=False))