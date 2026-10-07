import pandas as pd

from sqlalchemy import create_engine

from datetime import datetime

from ml4 import predict_churn


# ---------------------------------------
# Database Connection
# ---------------------------------------

DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/friday"
)

engine = create_engine(DATABASE_URL)


# ---------------------------------------
# Load ML Features
# ---------------------------------------

df = pd.read_sql(
    """
    SELECT *
    FROM customer_ml_features
    """,
    engine
)

print("\nCUSTOMERS LOADED")
print(len(df))

print("\nCOLUMNS")
print(df.columns.tolist())


# ---------------------------------------
# Score Function
# ---------------------------------------

def score_customer(row):

    result = predict_churn(
        tenure=row["tenure"],
        monthly_charges=row["monthly_charges"],
        contract_type=row["contract_type"],
        internet_service=(
            row["internet_service"]
            if pd.notna(row["internet_service"])
            else "No"
        ),
        service_count=row["service_count"]
    )

    return pd.Series(
        {
            "risk_score":
            result["risk_score"],

            "prediction":
            result["prediction"],

            "confidence":
            result["confidence"]
        }
    )


# ---------------------------------------
# Score Everyone
# ---------------------------------------

scores = df.apply(
    score_customer,
    axis=1
)

df = pd.concat(
    [df, scores],
    axis=1
)


# ---------------------------------------
# Add Scoring Date
# ---------------------------------------

df["scoring_date"] = (
    datetime.today()
    .strftime("%Y-%m-%d")
)


# ---------------------------------------
# Final Risk Table
# ---------------------------------------

risk_table = df[
    [
        "customer_id",
        "risk_score",
        "prediction",
        "confidence",
        "scoring_date"
    ]
]


# ---------------------------------------
# Save To SQL
# ---------------------------------------

risk_table.to_sql(
    "customer_risk_table",
    engine,
    if_exists="replace",
    index=False
)

print(
    "\nPASS - customer_risk_table created"
)

print(
    f"Rows: {len(risk_table)}"
)


# ---------------------------------------
# Distribution
# ---------------------------------------

print("\nPREDICTION DISTRIBUTION")

distribution = (
    risk_table["prediction"]
    .value_counts()
)

print(distribution)

print("\nPERCENTAGE")

print(
    (
        risk_table["prediction"]
        .value_counts(normalize=True)
        * 100
    ).round(2)
)


# ---------------------------------------
# Top 10 Highest Risk
# ---------------------------------------

top10 = (
    risk_table
    .sort_values(
        "risk_score",
        ascending=False
    )
    .head(10)
)

print(
    "\nTOP 10 HIGHEST RISK CUSTOMERS"
)

print(top10)


# ---------------------------------------
# Compare With SQL6 View
# ---------------------------------------

try:

    sql6_df = pd.read_sql(
        """
        SELECT customer_id
        FROM v_high_risk_customers
        """,
        engine
    )

    overlap = len(
        set(top10["customer_id"])
        &
        set(sql6_df["customer_id"])
    )

    print(
        f"\nOverlap With SQL6 View: {overlap}/10"
    )

except Exception as e:

    print(
        "\nCould not compare with SQL6 view."
    )

    print(
        f"Error: {str(e)}"
    )