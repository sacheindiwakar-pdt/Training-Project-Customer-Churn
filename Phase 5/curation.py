import pandas as pd

from sqlalchemy import (
    create_engine,
    text
)

from cleaner import CustomerCleaner


DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/friday"
)

engine = create_engine(DATABASE_URL)


def clean_staging(engine):

    df_raw = pd.read_sql(
        "SELECT * FROM stg_customer_raw",
        engine
    )

    raw_count = len(df_raw)

    cleaner = CustomerCleaner(df_raw)

    df_clean = cleaner.clean()

    df_clean.to_sql(
        "cleaned_customers",
        engine,
        if_exists="replace",
        index=False
    )

    clean_count = len(df_clean)

    assert raw_count == clean_count, (
        f"Row count mismatch. "
        f"Raw={raw_count}, "
        f"Clean={clean_count}"
    )

    print(
        f"PASS - Row Count Check ({clean_count})"
    )


def quality_report(engine):

    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    print("\nQUALITY REPORT")
    print("-" * 40)

    null_customer_ids = (
        df["customer_id"]
        .isnull()
        .sum()
    )

    print(
        "PASS - customer_id NULL check"
        if null_customer_ids == 0
        else f"FAIL - {null_customer_ids}"
    )

    null_monthly = (
        df["monthly_charges"]
        .isnull()
        .sum()
    )

    print(
        "PASS - monthly_charges NULL check"
        if null_monthly == 0
        else f"FAIL - {null_monthly}"
    )

    invalid_churn = (
        ~df["churn"].isin([0, 1])
    ).sum()

    print(
        "PASS - churn values"
        if invalid_churn == 0
        else f"FAIL - {invalid_churn}"
    )


def build_curated_tables(engine):

    with engine.begin() as conn:

        conn.execute(
            text(
                "SET FOREIGN_KEY_CHECKS=0"
            )
        )

        conn.execute(
            text("""
            DROP TABLE IF EXISTS fact_customer_account
            """)
        )

        conn.execute(
            text("""
            DROP TABLE IF EXISTS customers
            """)
        )

        conn.execute(
            text("""
            DROP TABLE IF EXISTS dim_payment
            """)
        )

        conn.execute(
            text("""
            DROP TABLE IF EXISTS dim_contract
            """)
        )

        conn.execute(
            text(
                "SET FOREIGN_KEY_CHECKS=1"
            )
        )

        # --------------------------
        # DIM CONTRACT
        # --------------------------

        conn.execute(text("""
        CREATE TABLE dim_contract (
            contract_key INT AUTO_INCREMENT PRIMARY KEY,
            contract_name VARCHAR(100)
        )
        """))

        conn.execute(text("""
        INSERT INTO dim_contract
        (contract_name)

        SELECT DISTINCT contract
        FROM cleaned_customers
        """))

        # --------------------------
        # DIM PAYMENT
        # --------------------------

        conn.execute(text("""
        CREATE TABLE dim_payment (
            payment_key INT AUTO_INCREMENT PRIMARY KEY,
            payment_method VARCHAR(100)
        )
        """))

        conn.execute(text("""
        INSERT INTO dim_payment
        (payment_method)

        SELECT DISTINCT payment_method
        FROM cleaned_customers
        """))

        # --------------------------
        # CUSTOMERS
        # --------------------------

        conn.execute(text("""
        CREATE TABLE customers AS

        SELECT
            customer_id,
            gender,
            senior_citizen,
            partner,
            dependents

        FROM cleaned_customers
        """))

        # --------------------------
        # FACT TABLE
        # --------------------------

        conn.execute(text("""
        CREATE TABLE fact_customer_account AS

        SELECT

            cl.customer_id,

            cl.tenure,

            cl.monthly_charges,

            cl.total_charges,

            cl.churn,

            dc.contract_key,

            dp.payment_key

        FROM cleaned_customers cl

        JOIN dim_contract dc
          ON cl.contract =
             dc.contract_name

        JOIN dim_payment dp
          ON cl.payment_method =
             dp.payment_method
        """))

    print(
        "PASS - Curated tables created"
    )


if __name__ == "__main__":

    clean_staging(engine)

    quality_report(engine)

    build_curated_tables(engine)