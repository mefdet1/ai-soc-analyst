import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix

import joblib

print("Loading data for evaluation...\n")
df = pd.read_csv('ml_ready_logs.csv')


# rule_1 = (df['is_managed'] == 0) & (df['is_compliant'] == 0) & (df['Status_Success'] == 1)
rule_2 = (df['hour_of_day'] >= 2) & (df['hour_of_day'] <= 4) & (df['Operating System_Windows'] == 0) & (df['Operating System_MacOs'] == 0)
rule_3 = (df['Browser_IE'] == 1) | (df['Browser_Unknown'] == 1) & (df['Status_Success'] == 0) 
df['legacy_is_malicious'] = np.where(rule_2 | rule_3, 1, 0)


X = df.drop(columns=['legacy_is_malicious'])
y = df['legacy_is_malicious']


rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X, y)
df['rf_prediction'] = rf_model.predict(X)


if_model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
if_model.fit(X)
df['if_anomaly'] = np.where(if_model.predict(X) == -1, 1, 0)




print("--------------------------------------------------")
print("1. SUPERVISED MODEL: RANDOM FOREST EVALUATION")
print("--------------------------------------------------")

tn, fp, fn, tp = confusion_matrix(y, df['rf_prediction']).ravel()

print(f"True Positives (Caught Attacks):      {tp}")
print(f"True Negatives (Ignored Safe Logs):   {tn}")
print(f"False Positives (False Alarms):       {fp}")
print(f"False Negatives (Missed Attacks):     {fn}\n")


print("Detailed Metrics:")
print(classification_report(y, df['rf_prediction'], target_names=['Safe (0)', 'Malicious (1)']))





print("\n--------------------------------------------------")
print("2. UNSUPERVISED MODEL: ISOLATION FOREST OVERLAP")
print("--------------------------------------------------")

ai_caught_known = df[(df['legacy_is_malicious'] == 1) & (df['if_anomaly'] == 1)]
print(f"Total Legacy Threats: {y.sum()}")
print(f"Legacy Threats caught by AI without rules: {len(ai_caught_known)}")





print("\n--------------------------------------------------")
print("3. SECURITY BLIND SPOTS REVEALED BY AI")
print("--------------------------------------------------")

blind_spots = df[(df['legacy_is_malicious'] == 0) & (df['if_anomaly'] == 1)]
print(f"Total Blind Spots Found: {len(blind_spots)}")

if len(blind_spots) > 0:
    print("\nSample of top 5 Blind Spots (Logs the legacy rules thought were safe):")
    
    columns_to_show = ['hour_of_day', 'day_of_week', 'is_managed', 'Status_Success']
    
    extra_cols = [c for c in df.columns if 'Browser' in c or 'Operating System' in c][:3]
    print(blind_spots[columns_to_show + extra_cols].head())
    
    
    blind_spots.to_csv('model_blind_spots.csv', index=False)
    print("\n>> Full blind spots exported to 'model_blind_spots.csv'")


joblib.dump(if_model, 'isolation_forest_model.pkl')
print("Model sucessfully saved as 'isolation_forest_model.pkl'")