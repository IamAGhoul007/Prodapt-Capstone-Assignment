import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = "d:/network labs/telecom-intelligence/ml/model.pkl"

def generate_and_train():
    print("Generating synthetic training data...")
    n_samples = 1000
    
    data = {
        'avg_calls': np.random.uniform(0, 5000, n_samples),
        'growth_rate': np.random.uniform(0, 1.0, n_samples),
        'variability': np.random.uniform(0, 1.0, n_samples),
        'peak_ratio': np.random.uniform(1.0, 3.0, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Simple logic for risk labels
    # Risk score = usage * (1 + growth) * (1 + variability)
    risk_score = df['avg_calls'] * (1 + df['growth_rate']) * (1 + df['variability'])
    
    q70 = risk_score.quantile(0.7)
    q90 = risk_score.quantile(0.9)
    
    df['risk_label'] = risk_score.apply(lambda x: 2 if x > q90 else (1 if x > q70 else 0))
    
    print("Training model...")
    X = df[['avg_calls', 'growth_rate', 'variability', 'peak_ratio']]
    y = df['risk_label']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    print(f"Saving model to {MODEL_PATH}...")
    joblib.dump(model, MODEL_PATH)
    print("Model retrained successfully.")

if __name__ == "__main__":
    generate_and_train()
