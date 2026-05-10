import pandas as pd
from sqlalchemy import create_engine
import os

DB_URL = os.getenv("DB_URL", "sqlite:///d:/network labs/telecom-intelligence/warehouse/telecom.db")
PROCESSED_PATH = "d:/network labs/telecom-intelligence/data/processed/usage_data"
REGION_PATH = "d:/network labs/telecom-intelligence/data/raw/region_mapping.csv"

def load():
    engine = create_engine(DB_URL)
    
    # Region Dim
    df_reg = pd.read_csv(REGION_PATH).rename(columns={'grid_id': 'region_id'})
    df_reg.to_sql('dim_region', engine, if_exists='replace', index=False)
    
    # Time Dim
    df_usage = pd.read_parquet(PROCESSED_PATH)
    df_usage['timestamp'] = pd.to_datetime(df_usage['timestamp'])
    
    df_time = df_usage[['timestamp']].drop_duplicates()
    df_time['time_id'] = df_time['timestamp'].dt.strftime('%Y%m%d%H').astype(int)
    df_time['date'] = df_time['timestamp'].dt.date
    df_time['hour'] = df_time['timestamp'].dt.hour
    df_time['day'] = df_time['timestamp'].dt.day
    df_time['month'] = df_time['timestamp'].dt.month
    df_time['weekday'] = df_time['timestamp'].dt.day_name()
    df_time.drop(columns=['timestamp']).drop_duplicates('time_id').to_sql('dim_time', engine, if_exists='replace', index=False)
    
    # Fact Table
    df_usage['time_id'] = df_usage['timestamp'].dt.strftime('%Y%m%d%H').astype(int)
    df_usage['region_id'] = df_usage['grid_id']
    df_fact = df_usage[['time_id', 'region_id', 'total_calls', 'total_sms', 'internet_usage']].rename(columns={
        'total_calls': 'call_count', 'total_sms': 'sms_count', 'internet_usage': 'internet_mb'
    })
    df_fact.insert(0, 'usage_id', range(1, 1 + len(df_fact)))
    df_fact.to_sql('fact_usage', engine, if_exists='replace', index=False)

if __name__ == "__main__":
    load()
