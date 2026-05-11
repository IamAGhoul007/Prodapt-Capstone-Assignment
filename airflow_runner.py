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

def detect_files():
    logger.info("Task: detect_files - Started")
    files = [f for f in os.listdir(LANDING) if f.endswith('.csv')]
    logger.info(f"Detected {len(files)} files: {files}")
    return files

def validate_files(files):
    logger.info("Task: validate_files - Started")
    valid, invalid = [], []
    cols = ['datetime', 'CellID', 'countrycode', 'smsin', 'smsout', 'callin', 'callout', 'internet']
    for f in files:
        try:
            df = pd.read_csv(os.path.join(LANDING, f), nrows=5)
            if all(c in df.columns for c in cols):
                valid.append(f)
            else:
                invalid.append(f)
        except Exception as e:
            logger.error(f"Error validating {f}: {e}")
            invalid.append(f)
    logger.info(f"Validation complete: {len(valid)} valid, {len(invalid)} invalid")
    return valid, invalid

def move_files(valid, invalid):
    logger.info("Task: move_files - Started")
    for f in valid:
        dest = os.path.join(RAW, f)
        if os.path.exists(dest): os.remove(dest) # Ensure we can move
        shutil.move(os.path.join(LANDING, f), dest)
        logger.info(f"Moved {f} to RAW")
    for f in invalid:
        dest = os.path.join(REJECTED, f)
        if os.path.exists(dest): os.remove(dest)
        shutil.move(os.path.join(LANDING, f), dest)
        logger.info(f"Moved {f} to REJECTED")

def run_job(name, script):
    logger.info(f"Task: {name} - Started")
    # Using the venv python to run the jobs
    python_exe = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")
    res = subprocess.run([python_exe, script], capture_output=True, text=True)
    if res.returncode != 0:
        logger.error(f"{name} failed: {res.stderr}")
        raise Exception(f"Job {name} failed")
    logger.info(f"{name} completed successfully")
    if res.stdout:
        logger.info(f"Output: {res.stdout[:500]}...")

def main():
    logger.info("=== Starting Pipeline Runner (Airflow Mock) ===")
    
    # 1. Detect
    files = detect_files()
    if not files:
        logger.info("No files to process. Exiting.")
        return

    # 2. Validate
    valid, invalid = validate_files(files)
    
    # 3. Move
    move_files(valid, invalid)
    
    if not valid:
        logger.info("No valid files to process in Spark. Exiting.")
        return

    # 4. Run Spark
    try:
        run_job("run_spark", SPARK_SCRIPT)
    except Exception as e:
        logger.error(f"Spark job failed: {e}")
        return

    # 5. Load Warehouse
    try:
        run_job("load_db", WAREHOUSE_SCRIPT)
    except Exception as e:
        logger.error(f"Warehouse load failed: {e}")
        return

    logger.info("=== Pipeline Completed Successfully ===")

if __name__ == "__main__":
    main()
