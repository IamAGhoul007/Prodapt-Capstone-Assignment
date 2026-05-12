import sys
import os

# Add local libs to path for WSL Airflow
LIBS_PATH = "/home/hp/airflow_libs"
if LIBS_PATH not in sys.path:
    sys.path.insert(0, LIBS_PATH)

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import shutil
import pandas as pd
import subprocess
import logging

# Paths - Using WSL paths for actual Airflow
BASE_DIR = "/mnt/d/network labs/telecom-intelligence"
LANDING = os.path.join(BASE_DIR, "data/landing/")
RAW = os.path.join(BASE_DIR, "data/raw/")
REJECTED = os.path.join(BASE_DIR, "data/rejected/")
PROCESSED = os.path.join(BASE_DIR, "data/processed/")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 5, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='telecom_ingestion_pipeline_v2',
    default_args=default_args,
    description='Telecom Data Ingestion and Processing Pipeline',
    schedule=timedelta(minutes=5),
    catchup=False,
    is_paused_upon_creation=False
)

def detect_files():
    """Detect new CSV files in landing directory."""
    files = [f for f in os.listdir(LANDING) if f.endswith('.csv')]

    logging.info(f"Detected files: {files}")

    if not files:
        logging.info("No new files detected.")

    return files


def validate_files(**kwargs):
    """Validate schema and null values."""
    ti = kwargs['ti']

    files = ti.xcom_pull(task_ids='detect_files')

    expected_cols = [
        'datetime',
        'CellID',
        'countrycode',
        'smsin',
        'smsout',
        'callin',
        'callout',
        'internet'
    ]

    valid_files = []
    invalid_files = []

    for f in files:
        file_path = os.path.join(LANDING, f)

        try:
            df = pd.read_csv(file_path, nrows=10)

            # Schema validation
            if not all(col in df.columns for col in expected_cols):
                logging.warning(f"File {f} failed schema validation.")
                invalid_files.append(f)
                continue

            # Null validation
            if df[expected_cols].isnull().values.any():
                logging.warning(f"File {f} contains null values.")
                invalid_files.append(f)
                continue

            valid_files.append(f)

        except Exception as e:
            logging.error(f"Error validating file {f}: {e}")
            invalid_files.append(f)

    ti.xcom_push(key='valid_files', value=valid_files)
    ti.xcom_push(key='invalid_files', value=invalid_files)

    return len(valid_files) > 0


def move_files(**kwargs):
    """Move valid and invalid files."""
    ti = kwargs['ti']

    valid_files = ti.xcom_pull(
        task_ids='validate_files',
        key='valid_files'
    )

    invalid_files = ti.xcom_pull(
        task_ids='validate_files',
        key='invalid_files'
    )

    for f in valid_files:
        src = os.path.join(LANDING, f)
        dst = os.path.join(RAW, f)

        shutil.move(src, dst)

        logging.info(f"Moved {f} to RAW")

    for f in invalid_files:
        src = os.path.join(LANDING, f)
        dst = os.path.join(REJECTED, f)

        shutil.move(src, dst)

        logging.info(f"Moved {f} to REJECTED")


def log_status(**kwargs):
    """Log ingestion status."""
    ti = kwargs['ti']

    valid = ti.xcom_pull(
        task_ids='validate_files',
        key='valid_files'
    )

    invalid = ti.xcom_pull(
        task_ids='validate_files',
        key='invalid_files'
    )

    logging.info(
        f"Ingestion Status: {len(valid)} valid, {len(invalid)} invalid."
    )


def run_spark_job():
    """Run Spark processing job."""
    script_path = os.path.join(
        BASE_DIR,
        "spark/telecom_pipeline.py"
    )

    try:
        logging.info(f"Running Spark job: {script_path}")

        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            check=True
        )

        logging.info(result.stdout)

    except subprocess.CalledProcessError as e:
        logging.error(f"Spark job failed: {e.stderr}")
        raise


def load_warehouse():
    """Load processed data into warehouse."""
    script_path = os.path.join(
        BASE_DIR,
        "warehouse/load_warehouse.py"
    )

    try:
        logging.info(f"Loading warehouse: {script_path}")

        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            check=True
        )

        logging.info(result.stdout)

    except subprocess.CalledProcessError as e:
        logging.error(f"Warehouse load failed: {e.stderr}")
        raise


def notify():
    """Notify completion."""
    logging.info("DAG executed successfully.")


# Tasks
t_detect = PythonOperator(
    task_id='detect_files',
    python_callable=detect_files,
    dag=dag
)

t_validate = PythonOperator(
    task_id='validate_files',
    python_callable=validate_files,
    dag=dag
)

t_move = PythonOperator(
    task_id='move_files',
    python_callable=move_files,
    dag=dag
)

t_log = PythonOperator(
    task_id='log_status',
    python_callable=log_status,
    dag=dag
)

t_spark = PythonOperator(
    task_id='run_spark_job',
    python_callable=run_spark_job,
    dag=dag
)

t_load = PythonOperator(
    task_id='load_warehouse',
    python_callable=load_warehouse,
    dag=dag
)

t_notify = PythonOperator(
    task_id='notify',
    python_callable=notify,
    dag=dag
)

# DAG Flow
(
    t_detect
    >> t_validate
    >> t_move
    >> t_log
    >> t_spark
    >> t_load
    >> t_notify
)