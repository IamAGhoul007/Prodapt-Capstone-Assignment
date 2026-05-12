import sqlite3
import random

DB_PATH = 'd:/network labs/telecom-intelligence/warehouse/telecom.db'

def fix_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Cleaning database...")
    cursor.execute("DELETE FROM fact_usage")
    cursor.execute("DELETE FROM dim_region")
    cursor.execute("DELETE FROM dim_time")

    regions = ['MILANO', 'ROMA', 'NAPOLI', 'TORINO', 'PALERMO', 'GENOVA', 'BOLOGNA', 'FIRENZE', 'BARI', 'CATANIA', 'VENEZIA', 'VICENZA']
    
    print("Populating dim_region...")
    for i, name in enumerate(regions):
        cursor.execute("INSERT INTO dim_region (region_id, region_name) VALUES (?, ?)", (i + 1, name))

    print("Populating dim_time...")
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for hour in range(24):
        time_id = int(f"20260512{hour:02d}")
        cursor.execute("INSERT INTO dim_time (time_id, date, hour, day, month, weekday) VALUES (?, ?, ?, ?, ?, ?)", 
                       (time_id, '2026-05-12', hour, 12, 5, 'Wednesday'))

    print("Populating fact_usage with varied data...")
    usage_id = 1
    for region_id in range(1, len(regions) + 1):
        # Give each region a different baseline
        base_calls = random.randint(100, 1000)
        base_sms = random.randint(200, 800)
        base_mb = random.randint(1000, 5000)
        
        for hour in range(24):
            time_id = int(f"20260512{hour:02d}")
            # Add some hourly variation
            multiplier = 1.0 + 0.5 * (1.0 if 8 <= hour <= 22 else 0.2)
            
            calls = base_calls * multiplier * random.uniform(0.8, 1.2)
            sms = base_sms * multiplier * random.uniform(0.8, 1.2)
            mb = base_mb * multiplier * random.uniform(0.8, 1.2)
            
            cursor.execute("INSERT INTO fact_usage (usage_id, time_id, region_id, call_count, sms_count, internet_mb) VALUES (?, ?, ?, ?, ?, ?)",
                           (usage_id, time_id, region_id, round(calls, 2), round(sms, 2), round(mb, 2)))
            usage_id += 1

    conn.commit()
    conn.close()
    print("Database fixed and populated successfully.")

if __name__ == "__main__":
    fix_db()
