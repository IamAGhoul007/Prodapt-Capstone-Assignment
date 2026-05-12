# PySpark Setup Guide (Windows)

This guide provides instructions on how to set up PySpark for the Telecom Network Intelligence project, especially for first-time users on Windows.

## 1. Prerequisites

### A. Java Development Kit (JDK)
PySpark requires Java. 
- **Download**: [Oracle JDK 21](https://www.oracle.com/java/technologies/downloads/#java21) or [OpenJDK](https://adoptium.net/).
- **Verify**: Open PowerShell and run `java -version`.
- **Environment Variable**: 
  - Set `JAVA_HOME` to your JDK installation path (e.g., `C:\Program Files\Java\jdk-21`).
  - Add `%JAVA_HOME%\bin` to your system `PATH`.

### B. Python
Ensure Python 3.9+ is installed.
- **Verify**: Run `python --version`.

### C. Hadoop Winutils (Required for Windows)
Spark needs `winutils.exe` to handle local file system operations correctly on Windows.
1. Create a folder `C:\hadoop\bin`.
2. Download `winutils.exe` for Hadoop 3.3.0+ from a trusted source (e.g., [cdarlint/winutils](https://github.com/cdarlint/winutils)).
3. Place `winutils.exe` in `C:\hadoop\bin`.
4. **Environment Variable**:
   - Set `HADOOP_HOME` to `C:\hadoop`.
   - Add `%HADOOP_HOME%\bin` to your system `PATH`.

---

## 2. Project Setup

1. **Create Virtual Environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
   *Note: This includes `pyspark`, `pandas`, `pyarrow`, and `fastparquet`.*

---

## 3. Running the Spark Tasks

### A. Verify Spark Installation
Run the test script to ensure Spark can initialize and read files:
```powershell
.\venv\Scripts\python spark/test_spark.py
```

### B. Run the Full Pipeline
The pipeline processes raw CDR data from `data/landing`, validates it, and performs ETL using PySpark.
```powershell
.\venv\Scripts\python airflow_runner.py
```
*Note: This script mocks the Airflow orchestration flow.*

---

## 4. Troubleshooting

- **ConnectionRefusedError**: If you see `WinError 10061`, it usually means the Spark driver failed to start or was blocked by a firewall. Ensure Java is allowed through the firewall.
- **HADOOP_HOME not set**: If you see warnings about `winutils.exe`, ensure the `HADOOP_HOME` environment variable is set and points to a folder containing a `bin` directory with `winutils.exe`.
- **Memory Issues**: The pipeline uses Spark's native `.write.parquet()` method to avoid driver OOM errors. If you need to collect data to the driver, use `.limit()` or ensure sufficient memory is allocated.
- **Large Datasets**: For very large datasets, adjust Spark memory in `spark/telecom_pipeline.py` by adding `.config("spark.driver.memory", "4g")` to the SparkSession builder.
