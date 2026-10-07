import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split

# --------------------------------------------------
# Database Connection
# --------------------------------------------------

DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/friday"
)

engine = create_engine(DATABASE_URL)

# --------------------------------------------------
# Load Features Table
# --------------------------------------------------

df = pd.read_sql(
    """
    SELECT *
    FROM customer_ml_features
    """,
    engine
)

print("\nDATASET SHAPE")
print(df.shape)

# --------------------------------------------------
# Preserve Customer IDs
# --------------------------------------------------

customer_ids = df["customer_id"]

# --------------------------------------------------
# Target Variable
# --------------------------------------------------

y = df["churn"]

# --------------------------------------------------
# Feature Matrix
# --------------------------------------------------

X = df.drop(
    columns=[
        "customer_id",
        "churn"
    ]
)

# --------------------------------------------------
# Encode Categorical Columns
# --------------------------------------------------

object_cols = X.select_dtypes(
    include=["object"]
).columns.tolist()

print("\nCATEGORICAL COLUMNS")
print(object_cols)

X = pd.get_dummies(
    X,
    columns=object_cols,
    drop_first=False
)

# --------------------------------------------------
# Split (same as ML2)
# --------------------------------------------------

X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
    X,
    y,
    customer_ids,
    test_size=0.20,
    stratify=y,
    random_state=42
)

# --------------------------------------------------
# Load Best Model
# --------------------------------------------------

model = joblib.load(
    "models/tree_churn.pkl"
)

print("\nBEST MODEL LOADED")
print("Decision Tree")

# --------------------------------------------------
# Feature Importances
# --------------------------------------------------

importance = pd.Series(
    model.feature_importances_,
    index=X.columns
)

importance = (
    importance
    .sort_values(ascending=False)
)

print("\nTOP 10 FEATURE IMPORTANCES")

print(
    importance.head(10)
)

# --------------------------------------------------
# Plot Top 10
# --------------------------------------------------

top10 = importance.head(10)

plt.figure(figsize=(10, 6))

top10.sort_values().plot(
    kind="barh",
    color="steelblue"
)

plt.title(
    "Top 10 Feature Importances"
)

plt.xlabel(
    "Importance"
)

plt.tight_layout()

plt.savefig(
    "top10_feature_importance.png"
)

plt.show()

print(
    "\nSaved: top10_feature_importance.png"
)

# --------------------------------------------------
# Top 3 Churn Drivers
# --------------------------------------------------

print("\nTOP 3 CHURN DRIVERS")

for feature in top10.index[:3]:

    print(feature)

# --------------------------------------------------
# Score Test Customers
# --------------------------------------------------

risk_scores = (
    model.predict_proba(X_test)
    [:, 1]
)

risk_df = pd.DataFrame(
    {
        "customer_id": id_test.values,
        "risk_score": risk_scores
    }
)

risk_df = (
    risk_df
    .sort_values(
        "risk_score",
        ascending=False
    )
)

# --------------------------------------------------
# Top 20 High Risk Customers
# --------------------------------------------------

top20 = risk_df.head(20)

print("\nTOP 20 HIGH-RISK CUSTOMERS")

print(top20)

top20.to_csv(
    "top20_risk_customers.csv",
    index=False
)

print(
    "\nSaved: top20_risk_customers.csv"
)

# --------------------------------------------------
# SQL6 Comparison
# --------------------------------------------------

try:

    sql6_df = pd.read_sql(
        """
        SELECT customer_id
        FROM v_high_risk_customers
        """,
        engine
    )

    overlap = len(
        set(top20["customer_id"])
        &
        set(sql6_df["customer_id"])
    )

    print(
        f"\nOverlap with SQL6 high-risk list: {overlap}/20"
    )

    overlap_customers = (
        set(top20["customer_id"])
        &
        set(sql6_df["customer_id"])
    )

    print("\nOVERLAPPING CUSTOMERS")

    for customer in overlap_customers:

        print(customer)

except Exception as e:

    print(
        "\nCould not compare with SQL6 view."
    )

    print(e)