import pandas as pd

from cp2 import CustomerCleaner

df = CustomerCleaner(pd.read_csv("telcom_churn.csv")).clean()

# Convert churn to numeric
df["churn"] = df["churn"].replace({
    "Yes": 1,
    "No": 0
})

# Service columns
service_cols = [
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies"
]

# Convert service columns to 0/1
for col in service_cols:
    df[col] = df[col].replace({
        "Yes": 1,
        "No": 0,
        "No internet service": 0
    })

# Feature 1: tenure_bucket
df["tenure_bucket"] = pd.cut(
    df["tenure"],
    bins=[0, 12, 24, 48, 72],
    labels=["0-12", "13-24", "25-48", "49-72"],
    include_lowest=True
)

# Numeric version for correlation
df["tenure_bucket_code"] = df["tenure_bucket"].cat.codes

# Feature 2: high_charge_flag
median_charge = df["monthly_charges"].median()
df["high_charge_flag"] = (df["monthly_charges"] > median_charge).astype(int)

# Feature 3: service_count
df["service_count"] = df[service_cols].sum(axis=1)

# Feature 4: is_long_term_customer
df["is_long_term_customer"] = (df["tenure"] >= 24).astype(int)

# Feature 5: has_streaming_bundle
df["has_streaming_bundle"] = (
    (df["streaming_tv"] == 1) &
    (df["streaming_movies"] == 1)
).astype(int)

# Feature 6: auto_pay_flag
df["auto_pay_flag"] = (
    df["payment_method"]
    .str.contains("automatic", case=False, na=False)
).astype(int)

# Correlations with churn
print("\nCorrelation of each new feature with churn:")

feature_cols = [
    "tenure_bucket_code",
    "high_charge_flag",
    "service_count",
    "is_long_term_customer",
    "has_streaming_bundle",
    "auto_pay_flag"
]

corr_table = {}

for col in feature_cols:
    corr = df[col].corr(df["churn"])
    corr_table[col] = corr
    print(f"{col}: {corr:.4f}")

# Drop helper column if not needed
df.drop(columns=["tenure_bucket_code"], inplace=True)

# Save final dataset
df.to_csv("customer_features.csv", index=False)

print("\ncustomer_features.csv saved with all original columns + 6 new feature columns")