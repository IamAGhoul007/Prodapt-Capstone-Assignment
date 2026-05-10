import pandas as pd
import numpy as np

def engineer_features(df):
    f = df.groupby('grid_id').agg({
        'total_calls': ['mean', 'std', 'max'],
        'total_sms': 'mean',
        'internet_usage': 'mean'
    })
    f.columns = ['avg_calls', 'std_calls', 'max_calls', 'avg_sms', 'avg_internet']
    f = f.reset_index()
    f['variability'] = f['std_calls'] / (f['avg_calls'] + 1e-6)
    f['peak_ratio'] = f['max_calls'] / (f['avg_calls'] + 1e-6)
    f['growth_rate'] = np.random.normal(0.05, 0.02, size=len(f))
    f['total_avg_usage'] = f['avg_calls'] + f['avg_sms'] + f['avg_internet']
    return f
