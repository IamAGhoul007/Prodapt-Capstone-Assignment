import sqlite3
import pandas as pd
import os

DB_PATH = "d:/network labs/telecom-intelligence/warehouse/telecom.db"

def verify_warehouse():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT r.region_name, t.hour, SUM(f.call_count) AS total_calls 
    FROM fact_usage f 
    JOIN dim_time t   ON f.time_id   = t.time_id 
    JOIN dim_region r ON f.region_id = r.region_id 
    GROUP BY r.region_name, t.hour 
    ORDER BY total_calls DESC 
    LIMIT 10;
    """
    
    try:
        print("Running verification query...")
        df = pd.read_sql_query(query, conn)
        if df.empty:
            print("Query returned no results. Ensure data is loaded.")
        else:
            print("Query results:")
            print(df.to_string(index=False))
    except Exception as e:
        print(f"Error running query: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_warehouse()
