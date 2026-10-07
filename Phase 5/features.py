import pandas as pd
from sqlalchemy import create_engine


def validate_features(engine, source_row_count):

    feature_df = pd.read_sql(
        "SELECT * FROM customer_ml_features",
        engine
    )

    feature_count = len(feature_df)

    print("\nFEATURE VALIDATION")
    print("-" * 40)

    if feature_count == source_row_count:

        print(
            f"PASS - Row Count ({feature_count})"
        )

    else:

        print(
            f"FAIL - Source={source_row_count}, Feature={feature_count}"
        )

    required_columns = [

        "churn",
        "tenure",
        "monthly_charges",
        "total_charges",
        "service_count",
        "high_charge_flag",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag",
        "contract_type",
        "internet_service"

    ]

    for col in required_columns:

        if col not in feature_df.columns:

            print(
                f"FAIL - Missing Column: {col}"
            )

            continue

        null_count = (
            feature_df[col]
            .isnull()
            .sum()
        )

        if null_count == 0:

            print(
                f"PASS - {col}"
            )

        else:

            print(
                f"FAIL - {col} contains {null_count} NULLs"
            )


def build_features(engine):

    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    service_columns = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies"
    ]

    df["service_count"] = (
        df[service_columns]
        .eq("Yes")
        .sum(axis=1)
    )

    median_charge = (
        df["monthly_charges"]
        .median()
    )

    df["high_charge_flag"] = (
        df["monthly_charges"]
        > median_charge
    ).astype(int)

    df["is_long_term_customer"] = (
        df["tenure"] >= 24
    ).astype(int)

    df["has_streaming_bundle"] = (
        (
            df["streaming_tv"] == "Yes"
        )
        &
        (
            df["streaming_movies"] == "Yes"
        )
    ).astype(int)

    auto_pay_methods = [
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ]

    df["auto_pay_flag"] = (
        df["payment_method"]
        .isin(auto_pay_methods)
    ).astype(int)

    feature_df = df[
        [
            "customer_id",
            "churn",
            "tenure",
            "monthly_charges",
            "total_charges",
            "service_count",
            "high_charge_flag",
            "is_long_term_customer",
            "has_streaming_bundle",
            "auto_pay_flag",
            "contract",
            "internet_service"
        ]
    ].copy()

    feature_df.rename(
        columns={
            "contract": "contract_type"
        },
        inplace=True
    )

    feature_df.to_sql(
        "customer_ml_features",
        engine,
        if_exists="replace",
        index=False
    )

    print(
        f"PASS - Features generated for {len(feature_df)} customers"
    )

    validate_features(
        engine,
        len(df)
    )


DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/friday"
)

engine = create_engine(DATABASE_URL)

if __name__ == "__main__":

    build_features(engine)