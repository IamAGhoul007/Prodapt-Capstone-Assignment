# Telecom Intelligence System

An end-to-end analytics platform for telecom network performance and risk prediction.

## System Architecture
- **Data Engineering**: PySpark ETL pipeline for processing massive network logs.
- **Orchestration**: Apache Airflow (running in WSL2 for Windows users).
- **Warehouse**: SQL-based star schema warehouse (SQLite).
- **Machine Learning**: Scikit-learn model for network congestion and risk prediction.
- **Backend**: FastAPI REST API providing analytics endpoints.
- **Frontend**: React-based dashboard for real-time visualization.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.11+**
- **Node.js & npm**
- **WSL2 (Ubuntu)** (For Airflow on Windows)

### 2. Environment Setup
Create and activate a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Starting the Services

#### A. Backend API
```powershell
python api/main.py
```
*Accessible at: http://localhost:8000/docs*

#### B. React Dashboard
```powershell
cd react-app
npm install
npm run dev
```
*Accessible at: http://localhost:5173*

#### C. Airflow Orchestration (via WSL)
Since Airflow requires a POSIX environment, it is set up to run in WSL (Ubuntu):

1. **Launch WSL**: `wsl -d Ubuntu`
2. **Set Environment**:
   ```bash
   export AIRFLOW_HOME="/mnt/d/network labs/telecom-intelligence/airflow"
   export PATH="/root/airflow_venv/bin:$PATH"
   ```
3. **Start Airflow**:
   ```bash
   airflow standalone
   ```
*UI Accessible at: http://localhost:8080*
*Credentials: User `admin` | Password `VvACkbVRxstqFnkH`*

#### D. Windows Native Pipeline (Alternative)
If you cannot use WSL, use the lightweight runner to execute the DAG logic:
```powershell
python airflow_runner.py
```

---

## 🛠 Project Structure
- `python/`: Scripts for exploratory data analysis.
- `spark/`: PySpark ETL logic (`telecom_pipeline.py`).
- `airflow/`: DAG definitions and orchestration logs.
- `warehouse/`: Database schema and loading logic.
- `api/`: FastAPI implementation.
- `react-app/`: Frontend source code.
- `ml/`: Model training and prediction logic.
- `data/`: Data directories (`landing/`, `raw/`, `processed/`, `rejected/`).

---

## 📊 Data Pipeline Flow
1. **Landing**: New CSV data arrives in `data/landing/`.
2. **Validation**: Airflow detects and validates the schema.
3. **Raw**: Valid files are moved to `data/raw/`.
4. **Spark ETL**: PySpark cleans, enriches, and aggregates data into Parquet format.
5. **Warehouse**: Processed data is loaded into the SQL Warehouse for API consumption.
