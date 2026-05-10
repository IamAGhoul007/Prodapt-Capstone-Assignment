# Telecom Intelligence

End-to-end system for telecom analytics and risk prediction.

## Modules
- `python/`: Initial EDA.
- `spark/`: ETL pipeline.
- `airflow/`: Orchestration.
- `warehouse/`: SQL Warehouse.
- `api/`: FastAPI backend.
- `react-app/`: Dashboard.
- `ml/`: Risk prediction model.

## Setup
1. `pip install -r requirements.txt`
2. `python spark/telecom_pipeline.py` (Run ETL)
3. `python warehouse/load_warehouse.py` (Load DB)
4. `python api/main.py` (Start API)
5. `cd react-app; npm install; npm run dev` (Start UI)
