import joblib, pandas as pd, os

PATH = "d:/network labs/telecom-intelligence/ml/model.pkl"

_model = None

def predict_usage_risk(features: dict) -> dict:
    global _model
    if _model is None:
        if not os.path.exists(PATH): return {"error": "No model"}
        _model = joblib.load(PATH)
    
    df = pd.DataFrame([{
        'avg_calls': features.get('avg_usage', 0),
        'growth_rate': features.get('growth_rate', 0),
        'variability': features.get('variability', 0),
        'peak_ratio': features.get('peak_ratio', 1.5)
    }])
    
    pred = _model.predict(df)[0]
    score = float(max(_model.predict_proba(df)[0]))
    risk = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}.get(pred, "UNKNOWN")
    
    return {"congestion_risk": risk, "anomaly_flag": risk == "HIGH", "score": score}

if __name__ == "__main__":
    print(predict_usage_risk({"avg_usage": 1500, "growth_rate": 0.1, "variability": 0.3, "peak_ratio": 1.2}))
