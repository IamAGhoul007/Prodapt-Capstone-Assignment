# Telecom Network Intelligence System - Design Document

## 1. Overview
The system provides a unified interface for network operators to monitor cell-tower activity and predict congestion risks. It handles high-volume time-series data from CDRs, SMS logs, and internet usage.

## 2. Architecture
The system follows a modern data engineering architecture:
- **Landing Layer**: Raw CSV files ingested from network logs.
- **Raw Layer**: Validated files ready for processing.
- **Processed Layer**: Cleaned and aggregated data stored in Parquet format, partitioned by date for performance.
- **Warehouse Layer**: A Star Schema implementation for analytical querying.
- **API Layer**: RESTful endpoints exposing warehouse data and ML predictions.
- **Frontend Layer**: A React dashboard for visualization.

## 3. Data Flow
1. **Ingestion**: Files land in `data/landing/`.
2. **Orchestration**: Airflow DAG detects, validates, and moves files to `data/raw/`.
3. **ETL**: PySpark job cleans data, joins with geo-metadata, and computes KPIs.
4. **Loading**: SQL script loads Parquet data into Fact and Dimension tables.
5. **Consumption**: FastAPI reads from SQL; React consumes FastAPI.

## 4. Batch vs Streaming Decisions
| Flow | Type | Justification |
|------|------|---------------|
| Network activity logs | Batch | High volume, processed daily for trend analysis. |
| Daily usage summary | Batch | Inherently a batch aggregation. |
| Monthly billing | Batch | Standard billing cycle. |
| Congestion alerts | Streaming | Requires real-time response to overload. |
| Customer dashboard | Batch/Hybrid | Views can be cached from daily batches. |

## 5. Storage Strategy
- **Raw (CSV)**: Retains original format for auditability and reprocessing.
- **Processed (Parquet)**: Columnar storage reduces IO for aggregation queries. Partitioning by date allows for efficient time-series analysis.
- **Warehouse (Star Schema)**: Simplifies joins and improves query performance for the dashboard.
