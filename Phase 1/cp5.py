import logging
from datetime import datetime
import pandas as pd

from cp2 import CustomerCleaner


# --------------------------------------------------
# LOGGING CONFIGURATION
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_data(filepath):

    try:
        logger.info("Starting data load: %s", filepath)

        df = pd.read_csv(filepath)

        logger.info(
            "Data loaded successfully. Rows: %s",
            len(df)
        )

        return df

    except Exception as e:

        logger.error(
            "Failed to load data: %s",
            e
        )

        raise


# --------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------

def build_features(df):

    try:

        logger.info(
            "Starting feature engineering."
        )

        # Convert churn to numeric

        df["churn"] = df["churn"].replace(
            {
                "Yes": 1,
                "No": 0
            }
        )

        # Service columns

        service_cols = [
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies"
        ]

        # Convert service columns to numeric

        for col in service_cols:

            df[col] = df[col].replace(
                {
                    "Yes": 1,
                    "No": 0,
                    "No internet service": 0
                }
            )

        # ----------------------------------
        # Feature 1: tenure_bucket
        # ----------------------------------

        df["tenure_bucket"] = pd.cut(
            df["tenure"],
            bins=[0, 12, 24, 48, 72],
            labels=[
                "0-12",
                "13-24",
                "25-48",
                "49-72"
            ],
            include_lowest=True
        )

        # ----------------------------------
        # Feature 2: high_charge_flag
        # ----------------------------------

        median_charge = (
            df["monthly_charges"]
            .median()
        )

        df["high_charge_flag"] = (
            df["monthly_charges"]
            > median_charge
        ).astype(int)

        # ----------------------------------
        # Feature 3: service_count
        # ----------------------------------

        df["service_count"] = (
            df[service_cols]
            .sum(axis=1)
        )

        # ----------------------------------
        # Feature 4: is_long_term_customer
        # ----------------------------------

        df["is_long_term_customer"] = (
            df["tenure"] >= 24
        ).astype(int)

        # ----------------------------------
        # Feature 5: has_streaming_bundle
        # ----------------------------------

        df["has_streaming_bundle"] = (
            (df["streaming_tv"] == 1)
            &
            (df["streaming_movies"] == 1)
        ).astype(int)

        # ----------------------------------
        # Feature 6: auto_pay_flag
        # ----------------------------------

        df["auto_pay_flag"] = (
            df["payment_method"]
            .str.contains(
                "automatic",
                case=False,
                na=False
            )
        ).astype(int)

        logger.info(
            "Feature engineering completed."
        )

        logger.info(
            "Feature dataset row count: %s",
            len(df)
        )

        return df

    except Exception as e:

        logger.error(
            "Feature engineering failed: %s",
            e
        )

        raise


# --------------------------------------------------
# DATA QUALITY CHECKS
# --------------------------------------------------

def validate_data_quality(df):

    try:

        logger.info(
            "Running data quality checks."
        )

        assert not (
            df["monthly_charges"]
            .isnull()
            .any()
        ), (
            "Data quality check failed: "
            "monthly_charges contains NULL values."
        )

        churn_values = set(
            df["churn"].unique()
        )

        assert churn_values.issubset(
            {0, 1}
        ), (
            "Data quality check failed: "
            "churn contains values other than 0/1."
        )

        logger.info(
            "All data quality checks passed."
        )

    except Exception as e:

        logger.error(
            "Data quality validation failed: %s",
            e
        )

        raise


# --------------------------------------------------
# SAVE OUTPUT FILES
# --------------------------------------------------

def save_outputs(
    clean_df,
    feature_df,
    output_dir="./"
):

    try:

        logger.info(
            "Saving output files."
        )

        timestamp = (
            datetime.now()
            .strftime("%Y%m%d")
        )

        clean_path = (
            f"{output_dir}/"
            f"cleaned_customer_{timestamp}.csv"
        )

        feature_path = (
            f"{output_dir}/"
            f"customer_features_{timestamp}.csv"
        )

        clean_df.to_csv(
            clean_path,
            index=False
        )

        feature_df.to_csv(
            feature_path,
            index=False
        )

        logger.info(
            "Cleaned file saved: %s",
            clean_path
        )

        logger.info(
            "Feature file saved: %s",
            feature_path
        )

        return (
            clean_path,
            feature_path
        )

    except Exception as e:

        logger.error(
            "Failed to save outputs: %s",
            e
        )

        raise


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def main():

    try:

        start_time = datetime.now()

        logger.info("=" * 60)
        logger.info(
            "CUSTOMER PIPELINE STARTED"
        )
        logger.info(
            "Start Time: %s",
            start_time
        )
        logger.info("=" * 60)

        input_file = "telcom_churn.csv"
        output_dir = "."

        # Step 1 - Load

        df = load_data(input_file)

        # Step 2 - Clean

        logger.info(
            "Starting data cleaning."
        )

        clean_df = (
            CustomerCleaner(df)
            .clean()
        )

        logger.info(
            "Cleaning completed."
        )

        logger.info(
            "Cleaned row count: %s",
            len(clean_df)
        )

        # Step 3 - Feature Engineering

        feature_df = build_features(
            clean_df.copy()
        )

        # Step 4 - Validation

        validate_data_quality(
            feature_df
        )

        # Step 5 - Save

        cleaned_path, feature_path = (
            save_outputs(
                clean_df,
                feature_df,
                output_dir
            )
        )

        end_time = datetime.now()

        duration = (
            end_time - start_time
        )

        logger.info("=" * 60)
        logger.info(
            "CUSTOMER PIPELINE COMPLETED"
        )
        logger.info(
            "End Time: %s",
            end_time
        )
        logger.info(
            "Duration: %s",
            duration
        )
        logger.info(
            "Cleaned Output: %s",
            cleaned_path
        )
        logger.info(
            "Feature Output: %s",
            feature_path
        )
        logger.info("=" * 60)

    except Exception as e:

        logger.exception(
            "PIPELINE FAILED: %s",
            e
        )

        raise


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()