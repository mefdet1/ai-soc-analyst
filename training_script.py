import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest


print("Loading clean dataset...")
df = pd.read_csv('ml_ready_logs.csv')



rule_1 = (df['is_managed'] == 0) & (df['is_compliant'] == 0) & (df['Status_Success'])


rule_2 = (df['hour_of_day'] >= 2) & (df['hour_of_day'] <= 5) & (df['Operating System_Windows'] == 0) & (df['Operating System_MacOs'] == 0)


rule_3 = (df['Browser_IE'] == 1) | (df['Browser_Unknown'] == 1)


df['legacy_is_malicious'] = np.where(rule_1 | rule_2 | rule_3, 1, 0)

print(f"Legacy Rules flagged {df['legacy_is_malicious'].sum()} logs as malicious.")


print("Training Supervised Random Forest...")
X_supervised = df.drop(columns=['legacy_is_malicious'])
y_supervised = df['legacy_is_malicious']

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_supervised, y_supervised)


df['rf_prediction'] = rf_model.predict(X_supervised)



print("Training Unsupervised Isolation Forest...")


X_unsupervised = df.drop(columns=['legacy_is_malicious', 'rf_prediction'])


if_model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
if_model.fit(X_unsupervised)


df['if_anomaly'] = np.where(if_model.predict(X_unsupervised) == -1, 1, 0)


print(f"Random Forest (Legacy Rules) Caught: {df['rf_prediction'].sum()}")
print(f"Isolation Forest (AI Anomaly) Caught: {df['if_anomaly'].sum()}")


blind_spots = df[(df['rf_prediction'] == 0) & (df['if_anomaly'] == 1)]

print(f"CRITICAL FINDING: The Isolation Forest caught {len(blind_spots)} anomalous logs that bypassed the legacy security rules.")


blind_spots.to_csv('presentation_blind_spots.csv', index=False)