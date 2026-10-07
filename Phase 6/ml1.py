import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/friday"
)

engine = create_engine(DATABASE_URL)

df = pd.read_sql(
    """
    SELECT *
    FROM customer_ml_features
    """,
    engine
)

print("\nDATASET SHAPE")
print(df.shape)

print("\nCOLUMNS")
print(df.columns.tolist())

# --------------------------
# Target
# --------------------------

y = df["churn"]

# --------------------------
# Drop ID + Target
# --------------------------

X = df.drop(
    columns=[
        "customer_id",
        "churn"
    ]
)

# --------------------------
# Numeric Features
# --------------------------

numeric_cols = [

    "tenure",

    "monthly_charges",

    "total_charges",

    "service_count",

    "high_charge_flag",

    "is_long_term_customer",

    "auto_pay_flag",

    "has_streaming_bundle"

]

print("\nNUMERIC FEATURES")
print(numeric_cols)

# --------------------------
# Categorical Features
# --------------------------

categorical_cols = [

    "contract_type",

    "internet_service"

]

print("\nCATEGORICAL FEATURES")
print(categorical_cols)

# --------------------------
# One Hot Encoding
# --------------------------

X = pd.get_dummies(
    X,
    columns=categorical_cols,
    drop_first=False
)

print("\nFINAL FEATURE COLUMNS")

for col in X.columns:
    print(col)

print("\nX SHAPE")
print(X.shape)

print("\ny SHAPE")
print(y.shape)

print("\nCLASS BALANCE")

balance = (
    y.value_counts(
        normalize=True
    )
)

print(balance)

print("\nCLASS PERCENTAGES")

print(
    (balance * 100)
    .round(2)
)

print("\nX SAMPLE")
print(X.head())

print("\nY SAMPLE")
print(y.head())