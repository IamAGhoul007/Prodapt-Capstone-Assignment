import os
import shutil
import pandas as pd
import subprocess
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = "d:/network labs/telecom-intelligence"
LANDING = f"{BASE_DIR}/data/landing/"
RAW = f"{BASE_DIR}/data/raw/"
REJECTED = f"{BASE_DIR}/data/rejected/"
SPARK_SCRIPT = f"{BASE_DIR}/spark/telecom_pipeline.py"
WAREHOUSE_SCRIPT = f"{BASE_DIR}/warehouse/load_warehouse.py"
PYTHON_EXE = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")

def detect_files():
    """6. detect_files(): list new CSVs in data/landing/."""
    logger.info("Task: detect_files - Started")
    files = [f for f in os.listdir(LANDING) if f.endswith('.csv')]
    logger.info(f"Detected {len(files)} files: {files}")
    return files

def validate_files(files):
    """7. validate_files(): check column match against expected schema, check nulls."""
    logger.info("Task: validate_files - Started")
    valid, invalid = [], []
    expected_cols = ['datetime', 'CellID', 'countrycode', 'smsin', 'smsout', 'callin', 'callout', 'internet']
    for f in files:
        try:
            df = pd.read_csv(os.path.join(LANDING, f), nrows=10)
            if all(col in df.columns for col in expected_cols) and not df[expected_cols].isnull().values.any():
                valid.append(f)
            else:
                invalid.append(f)
        except Exception as e:
            logger.error(f"Error validating {f}: {e}")
            invalid.append(f)
    logger.info(f"Validation complete: {len(valid)} valid, {len(invalid)} invalid")
    return valid, invalid

def move_files(valid, invalid):
    """8. move_files(): valid files -> data/raw/, invalid files -> data/rejected/."""
    logger.info("Task: move_files - Started")
    for f in valid:
        dest = os.path.join(RAW, f)
        if os.path.exists(dest): os.remove(dest)
        shutil.move(os.path.join(LANDING, f), dest)
        logger.info(f"Moved {f} to RAW")
    for f in invalid:
        dest = os.path.join(REJECTED, f)
        if os.path.exists(dest): os.remove(dest)
        shutil.move(os.path.join(LANDING, f), dest)
        logger.info(f"Moved {f} to REJECTED")

def log_status(valid, invalid):
    logger.info("Task: log_status - Started")
    logger.info(f"Ingestion Summary: {len(valid)} files accepted, {len(invalid)} files rejected.")

def run_spark_job():
    """9. run_spark_job(): wrap a call to telecom_pipeline.py."""
    logger.info("Task: run_spark_job - Started")
    res = subprocess.run([PYTHON_EXE, SPARK_SCRIPT], capture_output=True, text=True)
    if res.returncode != 0:
        logger.error(f"Spark job failed: {res.stderr}")
        return False
    logger.info("Spark job completed successfully")
    return True

def load_warehouse():
    """10. load_warehouse(): load processed Parquet into SQL warehouse tables."""
    logger.info("Task: load_warehouse - Started")
    res = subprocess.run([PYTHON_EXE, WAREHOUSE_SCRIPT], capture_output=True, text=True)
    if res.returncode != 0:
        logger.error(f"Warehouse load failed: {res.stderr}")
        return False
    logger.info("Warehouse load completed successfully")
    return True

def notify(success):
    """11. notify(): print or log success/failure."""
    logger.info("Task: notify - Started")
    if success:
        logger.info("PIPELINE SUCCESS: All tasks completed.")
    else:
        logger.error("PIPELINE FAILURE: One or more tasks failed.")

import time
import argparse

def main():
    parser = argparse.ArgumentParser(description='Telecom Pipeline Runner')
    parser.add_argument('--loop', action='store_true', help='Run in a loop every 5 minutes')
    args = parser.parse_args()

    while True:
        logger.info("=== Starting Telecom Pipeline Runner (Windows Airflow Emulator) ===")
        
        # detect_files >> validate_files >> move_files >> log_status >> run_spark_job >> load_warehouse >> notify
        
        files = detect_files()
        if not files:
            logger.info("No files to process.")
            notify(True)
        else:
            valid, invalid = validate_files(files)
            move_files(valid, invalid)
            log_status(valid, invalid)
            
            if not valid:
                logger.info("No valid files for Spark processing.")
                notify(True)
            else:
                success = run_spark_job()
                if success:
                    success = load_warehouse()
                notify(success)
        
        logger.info("=== Pipeline Execution Finished ===")
        
        if not args.loop:
            break
            
        logger.info("Sleeping for 5 minutes...")
        time.sleep(300) # 5 minutes

if __name__ == "__main__":
    main()
