from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, hour, date_format, sum as _sum, broadcast
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
import os

os.environ['HADOOP_HOME'] = os.path.abspath(".")

def create_session():
    return SparkSession.builder \
        .appName("TelecomNetworkIntelligence") \
        .config("spark.sql.shuffle.partitions", "20") \
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem") \
        .config("spark.hadoop.mapreduce.fileoutputcommitter.marksuccessfuljobs", "false") \
        .getOrCreate()

def load(spark, path):
    schema = StructType([
        StructField("datetime", StringType(), True),
        StructField("CellID", LongType(), True),
        StructField("countrycode", StringType(), True),
        StructField("smsin", DoubleType(), True),
        StructField("smsout", DoubleType(), True),
        StructField("callin", DoubleType(), True),
        StructField("callout", DoubleType(), True),
        StructField("internet", DoubleType(), True)
    ])
    
    if os.path.isdir(path):
        files = [os.path.join(path, f).replace("\\", "/") for f in os.listdir(path) if f.startswith("sms-call-internet-mi-") and f.endswith(".csv")]
        df = spark.read.csv(files, header=True, schema=schema)
    else:
        df = spark.read.csv(path, header=True, schema=schema)
    return df

def clean(df):
    df = df.filter(col("datetime") != "datetime")
    df = df.withColumnRenamed("datetime", "timestamp") \
           .withColumnRenamed("CellID", "grid_id") \
           .withColumnRenamed("countrycode", "country_code") \
           .withColumnRenamed("smsin", "sms_in") \
           .withColumnRenamed("smsout", "sms_out") \
           .withColumnRenamed("callin", "call_in") \
           .withColumnRenamed("callout", "call_out") \
           .withColumnRenamed("internet", "internet_usage")

    df = df.withColumn("timestamp", to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss"))
    df = df.filter((col("internet_usage") >= 0) | col("internet_usage").isNull())
    df = df.fillna(0, subset=["sms_in", "sms_out", "call_in", "call_out", "internet_usage"])
    df = df.withColumn("total_sms", col("sms_in") + col("sms_out")) \
           .withColumn("total_calls", col("call_in") + col("call_out"))
    return df

def enrich(spark, df, mapping_path):
    mapping_df = spark.read.csv(mapping_path, header=True, inferSchema=True)
    return df.join(broadcast(mapping_df), df.grid_id == mapping_df.grid_id, "left").drop(mapping_df.grid_id)

def aggregate(df):
    calls_per_hour = df.withColumn("hour", hour(col("timestamp"))) \
                       .groupBy("hour").agg(_sum("total_calls").alias("sum_calls")).orderBy("hour")
    sms_per_region_day = df.withColumn("date", date_format(col("timestamp"), "yyyy-MM-dd")) \
                           .groupBy("region_name", "date").agg(_sum("total_sms").alias("sum_sms"))
    internet_per_day = df.withColumn("date", date_format(col("timestamp"), "yyyy-MM-dd")) \
                         .groupBy("date").agg(_sum("internet_usage").alias("total_internet"))
    return {
        "calls_per_hour": calls_per_hour,
        "sms_per_region_day": sms_per_region_day,
        "internet_per_day": internet_per_day,
        "peak_hours": calls_per_hour.orderBy(col("sum_calls").desc()).limit(5)
    }

def write(df, summaries, output_path):
    pdf = df.withColumn("date", date_format(col("timestamp"), "yyyy-MM-dd")).toPandas()
    usage_data_path = os.path.join(output_path, "usage_data")
    if not os.path.exists(usage_data_path): os.makedirs(usage_data_path)
    pdf.to_parquet(usage_data_path, partition_cols=['date'], index=False)
    
    for name, s_df in summaries.items():
        summary_file = os.path.join(output_path, f"summary_{name}.parquet")
        s_df.toPandas().to_parquet(summary_file, index=False)

def main():
    spark = create_session()
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_path = os.path.join(base_path, "data", "raw").replace("\\", "/")
    mapping_path = os.path.join(raw_path, "region_mapping.csv").replace("\\", "/")
    processed_path = os.path.join(base_path, "data", "processed").replace("\\", "/")
    
    df = clean(load(spark, raw_path))
    df = enrich(spark, df, mapping_path)
    df.cache()
    df = df.repartition("region_name")
    
    summaries = aggregate(df)
    write(df, summaries, processed_path)
    spark.stop()

if __name__ == "__main__":
    main()
