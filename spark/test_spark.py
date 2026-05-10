from pyspark.sql import SparkSession
import os

spark = SparkSession.builder \
    .appName("Test") \
    .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem") \
    .getOrCreate()

path = "D:/network labs/telecom-intelligence/data/raw/sms-call-internet-mi-2013-11-01.csv"
try:
    df = spark.read.csv(path, header=True)
    print(f"Count: {df.count()}")
except Exception as e:
    print(f"Error: {e}")

spark.stop()
