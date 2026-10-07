import pandas as pd

# Import the CustomerCleaner class
from cp2 import CustomerCleaner

# ==========================================================
# Load and Clean Data
# ==========================================================
df = pd.read_csv("telcom_churn.csv")

cleaner = CustomerCleaner(df)
df = cleaner.clean()

# ==========================================================
# 1. Churn Rate by Contract Type
# ==========================================================
print("=" * 60)
print("CHURN RATE BY CONTRACT TYPE")
print("=" * 60)

contract_churn = (
    df.groupby("contract")["churn"]
      .mean()
      .sort_values(ascending=False) * 100
)

print(contract_churn)

print(f"\nHighest Churn Contract: {contract_churn.idxmax()}")

# ==========================================================
# 2. Churn Rate by Internet Service
# ==========================================================
print("\n" + "=" * 60)
print("CHURN RATE BY INTERNET SERVICE")
print("=" * 60)

internet_churn = (
    df.groupby("internet_service")["churn"]
      .mean()
      .sort_values(ascending=False) * 100
)

print(internet_churn)

# ==========================================================
# 3. Churn Rate by Payment Method
# ==========================================================
print("\n" + "=" * 60)
print("CHURN RATE BY PAYMENT METHOD")
print("=" * 60)

payment_churn = (
    df.groupby("payment_method")["churn"]
      .mean()
      .sort_values(ascending=False) * 100
)

print(payment_churn)

# ==========================================================
# 4. Churn Rate by Tenure Bucket
# ==========================================================
print("\n" + "=" * 60)
print("CHURN RATE BY TENURE BUCKET")
print("=" * 60)

df["tenure_bucket"] = pd.cut(
    df["tenure"],
    bins=[0, 12, 24, 48, 72],
    labels=["0-12", "13-24", "25-48", "49-72"],
    include_lowest=True
)

tenure_churn = (
    df.groupby("tenure_bucket")["churn"]
      .mean() * 100
)

print(tenure_churn)

# ==========================================================
# 5. Average Monthly Charges
# ==========================================================
print("\n" + "=" * 60)
print("AVERAGE MONTHLY CHARGES")
print("=" * 60)

avg_monthly = (
    df.groupby("churn")["monthly_charges"]
      .mean()
)

avg_monthly.index = ["Not Churned", "Churned"]

print(avg_monthly)

# ==========================================================
# 6. Highest Churn Combination
# ==========================================================
print("\n" + "=" * 60)
print("CONTRACT + INTERNET SERVICE")
print("=" * 60)

combo = (
    df.groupby(["contract", "internet_service"])["churn"]
      .mean()
      .sort_values(ascending=False) * 100
)

print(combo)

highest = combo.idxmax()
highest_rate = combo.max()

print(f"\nHighest Risk Combination:")
print(f"Contract         : {highest[0]}")
print(f"Internet Service : {highest[1]}")
print(f"Churn Rate       : {highest_rate:.2f}%")

# ==========================================================
# Business Summary
# ==========================================================
print("\n" + "=" * 60)
print("BUSINESS SUMMARY")
print("=" * 60)

print("""
1. Customers on month-to-month contracts show the highest churn rate, especially those using Fiber Optic internet service.
2. Electronic Check users generally churn more often than customers using other payment methods, and customers with shorter tenure are more likely to leave.
3. The retention team should prioritize proactive offers, loyalty rewards, and personalized engagement for new month-to-month Fiber Optic customers to reduce churn.
""")