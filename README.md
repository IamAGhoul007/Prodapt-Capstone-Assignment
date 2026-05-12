# Telecom Intelligence System

An end-to-end analytics platform for telecom network performance and risk prediction. This system integrates real-time data ingestion, PySpark processing, automated orchestration, and machine learning.

## 🛠 System Architecture
- **Data Engineering**: PySpark ETL pipeline for processing massive network logs.
- **Orchestration**: Apache Airflow (WSL2) or Native Windows Runner.
- **Warehouse**: SQL-based star schema warehouse (SQLite).
- **Machine Learning**: Scikit-learn Random Forest model for risk prediction.
- **Backend**: FastAPI REST API providing analytics and ML endpoints.
- **Frontend**: React (Vite) dashboard for real-time visualization.

---

## 🚀 Execution Guide (Step-by-Step)

Follow these steps in separate terminals to start the complete system.

### 1. Environment Setup (First time only)
Open a terminal in the project root:
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd react-app
npm install
cd ..
```

### 2. Orchestration & Data Pipeline (Choose ONE)

#### Option A: Native Windows Runner (Recommended for Quick Testing)
If you are on Windows and don't want to use WSL, use the provided emulator:
```powershell
.\venv\Scripts\activate
python airflow_runner.py --loop
```
*This script emulates the Airflow DAG behavior, checking `data/landing/` for new files every 5 minutes.*

#### Option B: Apache Airflow (WSL2 Ubuntu)
1.  Open your **WSL terminal** (Ubuntu).
2.  Run the following:
    ```bash
    export AIRFLOW_HOME="$(pwd)/airflow"
    airflow standalone
    ```
*UI Accessible at: [http://localhost:8080](http://localhost:8080) (User: `admin` | Password: `VvACkbVRxstqFnkH`)*

### 3. Start the Backend API
```powershell
.\venv\Scripts\activate
python api/main.py
```
*API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)*

### 4. Start the React Dashboard
```powershell
cd react-app
npm run dev
```
*Dashboard URL: [http://localhost:5173](http://localhost:5173)*

---

## 🧠 Machine Learning & Data Verification

### Model Retraining
If you find the prediction results are not sensitive enough, you can retrain the model with varied synthetic data:
```powershell
python scratch/retrain_model.py
```

### Database Health Check
To reset the database with fresh, varied sample data for visualization:
```powershell
python scratch/fix_db.py
```

---

## 📊 Data Pipeline Flow
The system processes data through the following stages:
1.  **Landing**: New CSVs arrive in `data/landing/`.
2.  **Validation**: Schema and null checks.
3.  **Spark Processing**: PySpark transforms raw data into Parquet in `data/processed/`.
4.  **Warehouse Load**: Processed data is loaded into the Star Schema (`telecom.db`).
5.  **Analytics**: API serves data to the React Dashboard.

---

## 📂 Project Structure
- `api/`: FastAPI source code.
- `react-app/`: Frontend React components.
- `airflow/`: Airflow DAGs and metadata.
- `ml/`: ML model (`model.pkl`) and prediction logic.
- `spark/`: PySpark ETL transformation scripts.
- `warehouse/`: SQLite database and schema.
- `data/`: Data storage layers (Landing, Raw, Processed, Rejected).
