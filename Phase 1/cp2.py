import pandas as pd
import numpy as np
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class CustomerCleaner:
    def __init__(self, df):
        """
        Initialize the CustomerCleaner with a DataFrame.
        """
        self.df = df.copy()
        logging.info("CustomerCleaner initialized.")

    def standardize_column_names(self):
        """
        Convert column names to lowercase snake_case.
        Example:
        MonthlyCharges -> monthly_charges
        """
        logging.info("Standardizing column names...")

        def to_snake_case(column):
            column = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', column)
            column = column.replace(" ", "_")
            return column.lower()

        self.df.columns = [to_snake_case(col) for col in self.df.columns]

        logging.info("Column names standardized.")

    def fix_total_charges(self):
        """
        Replace blank strings with NaN and convert total_charges to float.
        """
        logging.info("Fixing total_charges column...")

        try:
            affected_rows = self.df["total_charges"].astype(str).str.strip().eq("").sum()

            self.df["total_charges"] = (
                self.df["total_charges"]
                .replace(r'^\s*$', np.nan, regex=True)
            )

            self.df["total_charges"] = pd.to_numeric(
                self.df["total_charges"],
                errors="coerce"
            )

            logging.info(f"Rows affected: {affected_rows}")

        except Exception as e:
            logging.error(f"Unexpected error while fixing total_charges: {e}")

    def normalize_binary_columns(self):
        """
        Convert Yes/No values to 1/0.
        """
        logging.info("Normalizing binary columns...")

        binary_columns = [
            "partner",
            "dependents",
            "phone_service",
            "paperless_billing",
            "churn"
        ]

        mapping = {
            "Yes": 1,
            "No": 0
        }

        for col in binary_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].map(mapping)

        logging.info("Binary columns normalized.")

    def handle_nulls(self):
        """
        Fill null total_charges with monthly_charges.
        Justification:
        New customers with tenure=0 have no accumulated charges.
        """
        logging.info("Handling null values...")

        null_count = self.df["total_charges"].isna().sum()

        self.df["total_charges"].fillna(
            self.df["monthly_charges"],
            inplace=True
        )

        logging.info(f"Filled {null_count} null values in total_charges.")

    def clean(self):
        """
        Perform complete cleaning pipeline.
        """
        logging.info("Starting data cleaning pipeline...")

        self.standardize_column_names()
        self.fix_total_charges()
        self.normalize_binary_columns()
        self.handle_nulls()

        logging.info("Data cleaning completed.")

        return self.df


# ==========================================================
# Test Code
# ==========================================================
if __name__ == "__main__":

    # Load dataset
    df = pd.read_csv("telcom_churn.csv")

    print("=" * 60)
    print("BEFORE CLEANING")
    print("=" * 60)
    print("Shape:", df.shape)
    print("\nData Types:")
    print(df.dtypes)

    # Clean data
    cleaner = CustomerCleaner(df)
    cleaned_df = cleaner.clean()

    cleaned_df.to_csv("cleaned_telcom_churn.csv", index=False)

    print("\n" + "=" * 60)
    print("AFTER CLEANING")
    print("=" * 60)
    print("Shape:", cleaned_df.shape)
    print("\nData Types:")
    print(cleaned_df.dtypes)