import os
import csv
import shutil
import pandas as pd

from sqlalchemy import (
    create_engine,
    text
)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

LANDING_DIR = "data/landing"
RAW_DIR = "data/raw"
REJECTED_DIR = "data/rejected"

DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/friday"
)

engine = create_engine(DATABASE_URL)

EXPECTED_COLS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn"
]

def detect_files():

    csv_files = []

    for file in os.listdir(LANDING_DIR):

        if file.lower().endswith(".csv"):
            csv_files.append(
                os.path.join(
                    LANDING_DIR,
                    file
                )
            )

    return csv_files

def validate_schema(filepath):

    with open(
        filepath,
        newline="",
        encoding="utf-8"
    ) as f:

        header = next(csv.reader(f))

    is_valid = header == EXPECTED_COLS

    return is_valid, header

def load_to_staging(
    filepath,
    engine
):

    df = pd.read_csv(filepath)

    df.to_sql(
        "stg_customer_raw",
        engine,
        if_exists="replace",
        index=False
    )

    return len(df)

def log_ingestion(filename, status, rows, reason):

    query = text("""
        INSERT INTO ingestion_log
        (
            file_name,
            row_count,
            load_time,
            status,
            reason
        )
        VALUES
        (
            :file_name,
            :row_count,
            NOW(),
            :status,
            :reason
        )
    """)

    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "file_name": filename,
                "row_count": rows,
                "status": status,
                "reason": reason
            }
        )

def process_landing():

    files = detect_files()

    if not files:
        print("No files found.")
        return

    for filepath in files:

        filename = os.path.basename(
            filepath
        )

        print(
            f"Processing {filename}..."
        )

        valid, header = (
            validate_schema(filepath)
        )

        if valid:

            rows = load_to_staging(
                filepath,
                engine
            )

            log_ingestion(
                filename,
                "LOADED",
                rows,
                "Schema Valid"
            )

            shutil.move(
                filepath,
                os.path.join(
                    RAW_DIR,
                    filename
                )
            )

            print(
                f"LOADED - {rows} rows"
            )

        else:

            reason = (
                "Column mismatch"
            )

            log_ingestion(
                filename,
                "REJECTED",
                0,
                reason
            )

            shutil.move(
                filepath,
                os.path.join(
                    REJECTED_DIR,
                    filename
                )
            )

            print(
                f"REJECTED - {reason}"
            )

if __name__ == "__main__":

    process_landing()
