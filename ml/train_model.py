import pandas as pd
import joblib, os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from feature_engineering import engineer_features

DATA = "d:/network labs/telecom-intelligence/data/processed/usage_data"

def train():
    if not os.path.exists(DATA): return
    df = engineer_features(pd.read_parquet(DATA))
    
    t90, t70 = df['total_avg_usage'].quantile(0.9), df['total_avg_usage'].quantile(0.7)
    df['risk_label'] = df['total_avg_usage'].apply(lambda x: 2 if x > t90 else (1 if x > t70 else 0))
    
    X, y = df[['avg_calls', 'growth_rate', 'variability', 'peak_ratio']], df['risk_label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    model = RandomForestClassifier(n_estimators=100).fit(X_train, y_train)
    joblib.dump(model, "d:/network labs/telecom-intelligence/ml/model.pkl")

if __name__ == "__main__":
    train()
