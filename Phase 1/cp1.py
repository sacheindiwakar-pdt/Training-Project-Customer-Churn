import pandas as pd

# Load the dataset
df = pd.read_csv("telcom_churn.csv")

# 1. Print dataset shape
print("=" * 60)
print("Dataset Shape")
print("=" * 60)
print(df.shape) #rows and columns

# 2. Print column names and data types
print("\n" + "=" * 60)
print("Column Names and Data Types")
print("=" * 60)
print(df.dtypes) #shows columns and datatypes

# 3. Null values and null percentage
print("\n" + "=" * 60)
print("Null Values")
print("=" * 60)

null_count = df.isnull().sum()
null_percent = (null_count / len(df)) * 100
null_table = pd.DataFrame({
    "Null Count": null_count,
    "Null Percentage": null_percent
})

print(null_table)

# 4. Value counts for categorical columns
categorical_cols = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "InternetService",
    "Contract",
    "PaymentMethod",
    "Churn"
]

print("\n" + "=" * 60)
print("Categorical Column Analysis")
print("=" * 60)

for col in categorical_cols:
    print(f"\nColumn: {col}")
    print("Unique Values:")
    print(df[col].unique())

    print("\nValue Counts:")
    print(df[col].value_counts())

    print("\nProportion:")
    print(df[col].value_counts(normalize=True))

# 5. Churn distribution and churn rate
print("\n" + "=" * 60)
print("Churn Distribution")
print("=" * 60)

churn_counts = df["Churn"].value_counts()
print(churn_counts)

churn_rate = (df["Churn"] == "Yes").mean() * 100

print(f"\nChurn Rate: {churn_rate:.2f}%")
print(f"Non-Churn Rate: {100 - churn_rate:.2f}%")

# 6. Inspect TotalCharges
print("\n" + "=" * 60)
print("TotalCharges Inspection")
print("=" * 60)

print("Original Data Type:", df["TotalCharges"].dtype)

total_numeric = pd.to_numeric(df["TotalCharges"], errors="coerce")

print("NaN values after conversion:",
      total_numeric.isnull().sum())

# Replace column with numeric version (optional)
df["TotalCharges"] = total_numeric

# 7. Summary statistics
print("\n" + "=" * 60)
print("Numerical Summary")
print("=" * 60)

for col in ["tenure", "MonthlyCharges", "TotalCharges"]:
    print(f"\n{col}")
    print("Minimum :", df[col].min())
    print("Maximum :", df[col].max())
    print("Mean    :", df[col].mean())

# 8. Profiling Summary
print("\n" + "=" * 60)
print("Data Profiling Summary")
print("=" * 60)

print("""
1. Dataset contains 7043 rows and 21 columns.
2. customerID is only an identifier and should not be used as a machine learning feature.
3. TotalCharges is stored as an object because a few blank values exist; convert it using pd.to_numeric(errors='coerce').
4. Churn data is imbalanced: approximately 73% customers did not churn and 27% churned.
5. Always perform data profiling (data types, null values, unique values, and distributions) before cleaning or feature engineering.
""")