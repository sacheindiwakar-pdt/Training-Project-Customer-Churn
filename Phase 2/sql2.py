import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:root@localhost/friday"
)

df = pd.read_csv(
    "telcom_churn.csv",
    dtype={"TotalCharges": str}
)

df.to_sql(
    "stage_customer",
    engine,
    if_exists="replace",
    index=False

)

print("Data loaded successfully.")

