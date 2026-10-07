import os
import sys
import pandas as pd

# -----------------------------------------
# Environment Setup
# -----------------------------------------

os.environ["HADOOP_HOME"] = r"D:\Training\hadoop"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Important
os.environ["PATH"] += os.pathsep + r"D:\Training\hadoop\bin"

# -----------------------------------------
# Spark Imports
# -----------------------------------------

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)

from pyspark.sql.functions import (
    col,
    when,
    avg,
    count,
    regexp_replace
)

# -----------------------------------------
# Spark Session
# -----------------------------------------

spark = (
    SparkSession.builder
    .appName("CustomerChurnSparkAnalysis")
    .master("local[2]")
    .config("spark.driver.memory", "4g")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# -----------------------------------------
# Manual Schema
# -----------------------------------------

schema = StructType([
    StructField("customerID", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("SeniorCitizen", IntegerType(), True),
    StructField("Partner", StringType(), True),
    StructField("Dependents", StringType(), True),
    StructField("tenure", IntegerType(), True),
    StructField("PhoneService", StringType(), True),
    StructField("MultipleLines", StringType(), True),
    StructField("InternetService", StringType(), True),
    StructField("OnlineSecurity", StringType(), True),
    StructField("OnlineBackup", StringType(), True),
    StructField("DeviceProtection", StringType(), True),
    StructField("TechSupport", StringType(), True),
    StructField("StreamingTV", StringType(), True),
    StructField("StreamingMovies", StringType(), True),
    StructField("Contract", StringType(), True),
    StructField("PaperlessBilling", StringType(), True),
    StructField("PaymentMethod", StringType(), True),
    StructField("MonthlyCharges", DoubleType(), True),
    StructField("TotalCharges", StringType(), True),
    StructField("Churn", StringType(), True)
])

# -----------------------------------------
# Read CSV
# -----------------------------------------

CSV_PATH = r"data\raw\telcom_churn.csv"

df = (
    spark.read
    .option("header", True)
    .schema(schema)
    .csv(CSV_PATH)
)

print("\nSPARK SCHEMA")
df.printSchema()

# -----------------------------------------
# Compare with Pandas
# -----------------------------------------

pandas_df = pd.read_csv(CSV_PATH)

print("\nPANDAS DTYPES")
print(pandas_df.dtypes)

# -----------------------------------------
# Fix TotalCharges
# -----------------------------------------

df = df.withColumn(
    "TotalCharges",
    regexp_replace(
        col("TotalCharges"),
        r"^\s*$",
        ""
    )
)

df = df.withColumn(
    "TotalCharges",
    when(
        col("TotalCharges") == "",
        None
    ).otherwise(
        col("TotalCharges")
    )
)

df = df.withColumn(
    "TotalCharges",
    col("TotalCharges").cast(DoubleType())
)

# -----------------------------------------
# Churn Encoding
# -----------------------------------------

df = df.withColumn(
    "churn_encoded",
    when(
        col("Churn") == "Yes",
        1
    ).otherwise(0)
)

# -----------------------------------------
# Contract Summary
# -----------------------------------------

contract_summary = (
    df.groupBy("Contract")
    .agg(
        count("*").alias(
            "customer_count"
        ),
        avg(
            "churn_encoded"
        ).alias(
            "churn_rate"
        )
    )
)

print("\nCONTRACT SUMMARY")

contract_summary.show(
    truncate=False
)

# -----------------------------------------
# Internet Service Summary
# -----------------------------------------

internet_summary = (
    df.groupBy("InternetService")
    .agg(
        avg(
            "MonthlyCharges"
        ).alias(
            "avg_monthly_charges"
        ),
        avg(
            "churn_encoded"
        ).alias(
            "avg_churn_rate"
        )
    )
)

print("\nINTERNET SERVICE SUMMARY")

internet_summary.show(
    truncate=False
)

# -----------------------------------------
# Cross Validation
# -----------------------------------------

print(
    "\nCross-check the churn rates above with CP3 pandas results."
)

# -----------------------------------------
# Write Parquet
# -----------------------------------------

OUTPUT_PATH = r"data\spark_output\contract_summary"

try:

    (
        contract_summary
        .write
        .mode("overwrite")
        .partitionBy("Contract")
        .parquet(OUTPUT_PATH)
    )

    print(
        "\nParquet written successfully."
    )

    parquet_df = (
        spark.read
        .parquet(OUTPUT_PATH)
    )

    print("\nPARQUET SCHEMA")

    parquet_df.printSchema()

    row_count = parquet_df.count()

    print(
        f"\nParquet Row Count: {row_count}"
    )

    parquet_df.show()

    assert (
        row_count
        ==
        contract_summary.count()
    )

    print(
        "\nPASS - Parquet round-trip is clean"
    )

except Exception as e:

    print(
        "\nParquet write/read failed."
    )

    print(
        "Reason:"
    )

    print(e)

# -----------------------------------------
# Stop Spark
# -----------------------------------------

spark.stop()