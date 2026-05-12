import pandas as pd
import os
import glob

def load(path):
    cols = ['datetime', 'CellID', 'countrycode', 'smsin', 'smsout', 'callin', 'callout', 'internet']
    if os.path.isdir(path):
        files = glob.glob(os.path.join(path, "sms-call-internet-mi-*.csv"))
        return pd.concat([pd.read_csv(f) for f in files])
    return pd.read_csv(path)

def clean(df):
    df = df.rename(columns={
        'datetime': 'timestamp',
        'CellID': 'grid_id',
        'countrycode': 'country_code',
        'smsin': 'sms_in',
        'smsout': 'sms_out',
        'callin': 'call_in',
        'callout': 'call_out',
        'internet': 'internet_usage'
    })
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['internet_usage'] = df['internet_usage'].fillna(0)
    df = df[df['internet_usage'] >= 0]
    df[['sms_in', 'sms_out', 'call_in', 'call_out']] = df[['sms_in', 'sms_out', 'call_in', 'call_out']].fillna(0)
    df['total_sms'] = df['sms_in'] + df['sms_out']
    df['total_calls'] = df['call_in'] + df['call_out']
    return df

def enrich(df, mapping_path):
    mapping_df = pd.read_csv(mapping_path)
    return df.merge(mapping_df, on='grid_id', how='left')

def aggregate(df):
    df['hour'] = df['timestamp'].dt.hour
    df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    
    calls_per_hour = df.groupby('hour')['total_calls'].sum().reset_index()
    sms_per_region_day = df.groupby(['region_name', 'date'])['total_sms'].sum().reset_index()
    internet_per_day = df.groupby('date')['internet_usage'].sum().reset_index()
    peak_hours = calls_per_hour.sort_values('total_calls', ascending=False).head(5)
    
    return {
        "calls_per_hour": calls_per_hour,
        "sms_per_region_day": sms_per_region_day,
        "internet_per_day": internet_per_day,
        "peak_hours": peak_hours
    }

def write(df, summaries, output_path):
    df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    usage_data_path = os.path.join(output_path, "usage_data")
    if not os.path.exists(usage_data_path): os.makedirs(usage_data_path)
    df.to_parquet(usage_data_path, partition_cols=['date'], index=False, engine='pyarrow')
    
    for name, s_df in summaries.items():
        summary_file = os.path.join(output_path, f"summary_{name}.parquet")
        s_df.to_parquet(summary_file, index=False, engine='pyarrow')

def main():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_path = os.path.join(base_path, "data", "raw")
    mapping_path = os.path.join(raw_path, "region_mapping.csv")
    processed_path = os.path.join(base_path, "data", "processed")
    
    print("Loading data...")
    df = load(raw_path)
    print("Cleaning data...")
    df = clean(df)
    print("Enriching data...")
    df = enrich(df, mapping_path)
    print("Aggregating data...")
    summaries = aggregate(df)
    print("Writing results...")
    write(df, summaries, processed_path)
    print("ETL Complete!")

if __name__ == "__main__":
    main()
