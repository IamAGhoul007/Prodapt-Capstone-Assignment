-- Dimensions
CREATE TABLE dim_time (
    time_id BIGINT PRIMARY KEY,
    date DATE,
    hour INTEGER,
    day INTEGER,
    month INTEGER,
    weekday VARCHAR(10)
);

CREATE TABLE dim_region (
    region_id BIGINT PRIMARY KEY,
    region_name VARCHAR(100),
    city VARCHAR(100)
);

-- Fact table
CREATE TABLE fact_usage (
    usage_id BIGINT PRIMARY KEY,
    time_id BIGINT,
    region_id BIGINT,
    call_count INTEGER,
    sms_count INTEGER,
    internet_mb DOUBLE,
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
);
