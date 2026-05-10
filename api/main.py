from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
from sqlalchemy import create_engine, text
from fastapi.middleware.cors import CORSMiddleware
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml.predict import predict_usage_risk

app = FastAPI(title="Telecom API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_URL = os.getenv("DB_URL", "sqlite:///d:/network labs/telecom-intelligence/warehouse/telecom.db")
engine = create_engine(DB_URL)

class UsageSummary(BaseModel):
    total_calls: int; total_sms: int; total_internet_mb: float; peak_hour: int; busiest_region: str

class RegionUsage(BaseModel):
    region: str; hourly_distribution: List[dict]; trend: List[float]

class PeakTraffic(BaseModel):
    top_hours: List[dict]; top_regions: List[dict]

class PredictionRequest(BaseModel):
    region: str; avg_usage: float; growth_rate: float; variability: float

class PredictionResponse(BaseModel):
    congestion_risk: str; anomaly_flag: bool; score: float

def run_query(query: str, params: dict = {}):
    with engine.connect() as conn: return pd.read_sql(text(query), conn, params=params)

@app.get("/usage/summary", response_model=UsageSummary)
def get_summary():
    stats = run_query("SELECT SUM(call_count) as c, SUM(sms_count) as s, SUM(internet_mb) as i FROM fact_usage").iloc[0]
    peak = run_query("SELECT t.hour FROM fact_usage f JOIN dim_time t ON f.time_id = t.time_id GROUP BY t.hour ORDER BY SUM(f.call_count) DESC LIMIT 1").iloc[0]['hour']
    busy = run_query("SELECT r.region_name FROM fact_usage f JOIN dim_region r ON f.region_id = r.region_id GROUP BY r.region_name ORDER BY SUM(f.call_count) DESC LIMIT 1").iloc[0]['region_name']
    return {"total_calls": int(stats['c']), "total_sms": int(stats['s']), "total_internet_mb": float(stats['i']), "peak_hour": int(peak), "busiest_region": busy}

@app.get("/usage/region/{region}", response_model=RegionUsage)
def get_region(region: str):
    df = run_query("SELECT t.hour, AVG(f.call_count) as calls, AVG(f.sms_count) as sms, AVG(f.internet_mb) as internet_mb FROM fact_usage f JOIN dim_time t ON f.time_id = t.time_id JOIN dim_region r ON f.region_id = r.region_id WHERE r.region_name = :r GROUP BY t.hour ORDER BY t.hour", {"r": region})
    if df.empty: raise HTTPException(404, "Not found")
    return {"region": region, "hourly_distribution": df.to_dict('records'), "trend": df['calls'].tolist()}

@app.get("/usage/peak", response_model=PeakTraffic)
def get_peak():
    h = run_query("SELECT hour, SUM(call_count)+SUM(sms_count)+SUM(internet_mb) as total FROM fact_usage f JOIN dim_time t ON f.time_id = t.time_id GROUP BY hour ORDER BY total DESC LIMIT 5")
    r = run_query("SELECT region_name as region, SUM(call_count)+SUM(sms_count)+SUM(internet_mb) as total FROM fact_usage f JOIN dim_region r ON f.region_id = r.region_id GROUP BY region_name ORDER BY total DESC LIMIT 5")
    return {"top_hours": h.to_dict('records'), "top_regions": r.to_dict('records')}

@app.post("/predict-usage-risk", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    res = predict_usage_risk({"avg_usage": req.avg_usage, "growth_rate": req.growth_rate, "variability": req.variability, "peak_ratio": 1.5})
    if "error" in res: raise HTTPException(500, res["error"])
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
