import sys
import json
import pandas as pd
import joblib
import warnings

# supress scikit-learn warning so they dont corrupt JSON output
warnings.filterwarnings("ignore");


try:
    model = joblib.load('isolation_forest_model.pkl')
except Exception as e:
    print(json.dumps({"error": f"Failed to load model: {str(e)}"}))
    sys.exit(1)


try:
    
    input_data = json.loads(sys.argv[1])
    df_incoming = pd.DataFrame([input_data])

    expected_cols = model.feature_names_in_
    df_incoming = df_incoming.reindex(columns=expected_cols, fill_value=0)

    prediction = model.predict(df_incoming)[0]
    raw_score = model.decision_function(df_incoming)[0]

    is_anomalous = True if prediction == -1 else False
    
    result = {
        "risk_flag": is_anomalous,
        "anomaly_score": round(float(raw_score), 4),
        "status": "success"
    }
    print(json.dumps(result))

except Exception as e:
    print(json.dumps({"error": str(e)}))