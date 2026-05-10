import pandas as pd
import numpy as np

class UsageProcessor:
    def __init__(self):
        self.df = None

    def load_data(self, path):
        try:
            self.df = pd.read_csv(path)
            return self.df
        except Exception as e:
            print(f"Load error: {e}")
            return None

    def clean_data(self):
        if self.df is None: return

        self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        self.df['hour'] = self.df['datetime'].dt.hour
        self.df['day'] = self.df['datetime'].dt.date
        
        usage_cols = ['smsin', 'smsout', 'callin', 'callout', 'internet']
        for col in usage_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
        
        self.df['sms_count'] = self.df['smsin'] + self.df['smsout']
        self.df['call_count'] = self.df['callin'] + self.df['callout']
        self.df['internet_usage'] = self.df['internet']
        
        self.df = self.df[(self.df['sms_count'] >= 0) & 
                          (self.df['call_count'] >= 0) & 
                          (self.df['internet_usage'] >= 0)]

    def compute_daily_usage(self):
        if self.df is None: return None
        return self.df.groupby('day').agg({
            'sms_count': 'sum',
            'call_count': 'sum',
            'internet_usage': 'sum'
        }).reset_index()

    def compute_kpis(self):
        if self.df is None: return None
        
        region_usage = self.df.groupby('CellID').agg({
            'sms_count': 'sum',
            'call_count': 'sum',
            'internet_usage': 'sum'
        }).reset_index()
        
        hourly_avg = self.df.groupby('hour').agg({
            'sms_count': 'mean',
            'call_count': 'mean',
            'internet_usage': 'mean'
        }).reset_index()
        
        peak_hour = self.df.groupby('hour')['call_count'].sum().idxmax()
        
        return {
            'region_usage': region_usage,
            'hourly_avg': hourly_avg,
            'peak_hour': peak_hour
        }

def call_plan_api(customer_id):
    return {
        "customer_id": customer_id,
        "plan_name": "Premium Data Plan",
        "data_limit_gb": 50,
        "voice_minutes": "Unlimited",
        "sms_limit": "Unlimited"
    }

if __name__ == "__main__":
    processor = UsageProcessor()
    df = processor.load_data("../data/landing/sms-call-internet-mi-2013-11-01.csv")
    if df is not None:
        processor.clean_data()
        print(processor.compute_daily_usage().head())
        print(processor.compute_kpis()['peak_hour'])
