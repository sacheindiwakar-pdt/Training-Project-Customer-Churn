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


def log_pipeline_run(
    file_name,
    inserted,
    updated,
    unchanged
):

    with engine.begin() as conn:

        conn.execute(
            text("""
            INSERT INTO pipeline_run_log
            (
                file_name,
                rows_inserted,
                rows_updated,
                rows_unchanged,
                run_timestamp
            )
            VALUES
            (
                :file_name,
                :inserted,
                :updated,
                :unchanged,
                NOW()
            )
            """),
            {
                "file_name": file_name,
                "inserted": inserted,
                "updated": updated,
                "unchanged": unchanged
            }
        )


def upsert_customers(csv_file):

    source_df = pd.read_csv(csv_file)

    # -----------------------------
    # Apply existing cleaner
    # -----------------------------

    cleaner = CustomerCleaner(source_df)

    source_df = cleaner.clean()

    target_df = pd.read_sql(
        """
        SELECT *
        FROM cleaned_customers
        """,
        engine
    )

    inserted = 0
    updated = 0
    unchanged = 0

    target_map = {
        row["customer_id"]: row
        for _, row in target_df.iterrows()
    }

    with engine.begin() as conn:

        for _, row in source_df.iterrows():

            customer_id = row["customer_id"]

            if customer_id not in target_map:

                inserted += 1

            else:

                existing = target_map[customer_id]

                changed = False

                compare_cols = [
                    "tenure",
                    "monthly_charges",
                    "total_charges",
                    "partner",
                    "dependents",
                    "churn"
                ]

                for col in compare_cols:

                    old_val = existing[col]
                    new_val = row[col]

                    if pd.isna(old_val) and pd.isna(new_val):
                        continue

                    if old_val != new_val:
                        changed = True
                        break

                if changed:
                    updated += 1
                else:
                    unchanged += 1

            conn.execute(
                text("""
                INSERT INTO cleaned_customers
                (
                    customer_id,
                    gender,
                    senior_citizen,
                    partner,
                    dependents,
                    tenure,
                    monthly_charges,
                    total_charges,
                    churn
                )
                VALUES
                (
                    :customer_id,
                    :gender,
                    :senior_citizen,
                    :partner,
                    :dependents,
                    :tenure,
                    :monthly_charges,
                    :total_charges,
                    :churn
                )

                ON DUPLICATE KEY UPDATE

                    gender = VALUES(gender),
                    senior_citizen = VALUES(senior_citizen),
                    partner = VALUES(partner),
                    dependents = VALUES(dependents),
                    tenure = VALUES(tenure),
                    monthly_charges = VALUES(monthly_charges),
                    total_charges = VALUES(total_charges),
                    churn = VALUES(churn)
                """),
                {
                    "customer_id": row["customer_id"],
                    "gender": row["gender"],
                    "senior_citizen": int(
                        row["senior_citizen"]
                    ),
                    "partner": int(
                        row["partner"]
                    ),
                    "dependents": int(
                        row["dependents"]
                    ),
                    "tenure": int(
                        row["tenure"]
                    ),
                    "monthly_charges": float(
                        row["monthly_charges"]
                    ),
                    "total_charges": float(
                        row["total_charges"]
                    ),
                    "churn": int(
                        row["churn"]
                    )
                }
            )

    log_pipeline_run(
        csv_file,
        inserted,
        updated,
        unchanged
    )

    print("\nPIPELINE RUN SUMMARY")
    print("-" * 30)
    print(f"Inserted : {inserted}")
    print(f"Updated  : {updated}")
    print(f"Unchanged: {unchanged}")


if __name__ == "__main__":

    upsert_customers(
        "data/raw/telcom_churn.csv"
    )