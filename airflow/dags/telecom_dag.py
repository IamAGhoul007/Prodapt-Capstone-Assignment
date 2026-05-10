from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os, shutil, pandas as pd, subprocess

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 5, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('telecom_network_intelligence', default_args=default_args, schedule_interval=timedelta(days=1))

LANDING = "d:/network labs/telecom-intelligence/data/landing/"
RAW = "d:/network labs/telecom-intelligence/data/raw/"
REJECTED = "d:/network labs/telecom-intelligence/data/rejected/"

def detect_files():
    return [f for f in os.listdir(LANDING) if f.endswith('.csv')]

def validate_files(**kwargs):
    files = kwargs['ti'].xcom_pull(task_ids='detect_files')
    valid, invalid = [], []
    cols = ['datetime', 'CellID', 'countrycode', 'smsin', 'smsout', 'callin', 'callout', 'internet']
    for f in files:
        try:
            df = pd.read_csv(os.path.join(LANDING, f), nrows=5)
            if all(c in df.columns for c in cols): valid.append(f)
            else: invalid.append(f)
        except: invalid.append(f)
    kwargs['ti'].xcom_push(key='valid_files', value=valid)
    kwargs['ti'].xcom_push(key='invalid_files', value=invalid)
    return len(valid) > 0

def move_files(**kwargs):
    ti = kwargs['ti']
    for f in ti.xcom_pull(task_ids='validate_files', key='valid_files'):
        shutil.move(os.path.join(LANDING, f), os.path.join(RAW, f))
    for f in ti.xcom_pull(task_ids='validate_files', key='invalid_files'):
        shutil.move(os.path.join(LANDING, f), os.path.join(REJECTED, f))

def run_job(script):
    res = subprocess.run(["python", script], capture_output=True, text=True)
    if res.returncode != 0: raise Exception(f"Job failed: {res.stderr}")

t1 = PythonOperator(task_id='detect_files', python_callable=detect_files, dag=dag)
t2 = PythonOperator(task_id='validate_files', python_callable=validate_files, dag=dag)
t3 = PythonOperator(task_id='move_files', python_callable=move_files, dag=dag)
t4 = PythonOperator(task_id='run_spark', python_callable=lambda: run_job("d:/network labs/telecom-intelligence/spark/telecom_pipeline.py"), dag=dag)
t5 = PythonOperator(task_id='load_db', python_callable=lambda: run_job("d:/network labs/telecom-intelligence/warehouse/load_warehouse.py"), dag=dag)

t1 >> t2 >> t3 >> t4 >> t5
