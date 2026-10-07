import pandas as pd
import json
import logging
from datetime import datetime

# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

quality_results = []


# --------------------------------------------------
# Result Recorder
# --------------------------------------------------

def record_result(
    check_name,
    status,
    value_found,
    threshold,
    severity
):

    result = {
        "check_name": check_name,
        "status": status,
        "value_found": value_found,
        "threshold": threshold,
        "severity": severity
    }

    quality_results.append(result)

    message = (
        f"{check_name}: {status} "
        f"(value={value_found}, threshold={threshold})"
    )

    if status == "PASS":
        logging.info(message)

    else:

        if severity == "CRITICAL":
            raise Exception(
                f"CRITICAL QUALITY FAILURE: {message}"
            )

        logging.warning(message)


# --------------------------------------------------
# Check 1 - Null Rate
# --------------------------------------------------

def check_null_rate(
    df,
    col,
    threshold,
    severity="CRITICAL"
):

    null_rate = (
        df[col]
        .isna()
        .mean()
        * 100
    )

    status = (
        "PASS"
        if null_rate <= threshold
        else "FAIL"
    )

    record_result(
        f"null_rate_{col}",
        status,
        round(null_rate, 2),
        f"{threshold}%",
        severity
    )


# --------------------------------------------------
# Check 2 - Range Check
# --------------------------------------------------

def check_value_range(
    df,
    col,
    min_value,
    max_value,
    severity="CRITICAL"
):

    invalid_rows = len(
        df[
            (df[col] < min_value)
            |
            (df[col] > max_value)
        ]
    )

    status = (
        "PASS"
        if invalid_rows == 0
        else "FAIL"
    )

    record_result(
        f"value_range_{col}",
        status,
        invalid_rows,
        f"{min_value}-{max_value}",
        severity
    )


# --------------------------------------------------
# Check 3 - Allowed Values
# --------------------------------------------------

def check_allowed_values(
    df,
    col,
    allowed_set,
    severity="CRITICAL"
):

    invalid_rows = (
        ~df[col].isin(allowed_set)
    ).sum()

    status = (
        "PASS"
        if invalid_rows == 0
        else "FAIL"
    )

    record_result(
        f"allowed_values_{col}",
        status,
        int(invalid_rows),
        list(allowed_set),
        severity
    )


# --------------------------------------------------
# Check 4 - Row Count
# --------------------------------------------------

def check_row_count(
    df,
    expected_min,
    severity="CRITICAL"
):

    rows = len(df)

    status = (
        "PASS"
        if rows >= expected_min
        else "FAIL"
    )

    record_result(
        "row_count",
        status,
        rows,
        expected_min,
        severity
    )


# --------------------------------------------------
# Check 5 - Duplicate Check
# --------------------------------------------------

def check_no_duplicates(
    df,
    key_col,
    severity="CRITICAL"
):

    duplicates = (
        df[key_col]
        .duplicated()
        .sum()
    )

    status = (
        "PASS"
        if duplicates == 0
        else "FAIL"
    )

    record_result(
        f"duplicates_{key_col}",
        status,
        int(duplicates),
        0,
        severity
    )


# --------------------------------------------------
# Check 6 - Churn Distribution
# --------------------------------------------------

def check_churn_distribution(
    df,
    severity="WARNING"
):

    churn_rate = (
        (df["Churn"] == "Yes")
        .mean()
        * 100
    )

    status = (
        "PASS"
        if 10 <= churn_rate <= 50
        else "FAIL"
    )

    record_result(
        "churn_distribution",
        status,
        round(churn_rate, 2),
        "10-50%",
        severity
    )


# --------------------------------------------------
# Report Writer
# --------------------------------------------------

def write_quality_report():

    report = {
        "run_timestamp":
        datetime.now().isoformat(),

        "results":
        quality_results
    }

    with open(
        "quality_report.json",
        "w"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print(
        "\nPASS - quality_report.json created"
    )


# --------------------------------------------------
# Runner
# --------------------------------------------------

def run_quality_checks():

    df = pd.read_csv(
        "data/raw/telcom_churn.csv"
    )

    # -----------------------
    # Null Checks
    # -----------------------

    check_null_rate(
        df,
        "MonthlyCharges",
        0
    )

    check_null_rate(
        df,
        "tenure",
        0
    )

    # -----------------------
    # Range Checks
    # -----------------------

    check_value_range(
        df,
        "tenure",
        0,
        100
    )

    check_value_range(
        df,
        "MonthlyCharges",
        0.01,
        1000
    )

    # -----------------------
    # Allowed Values
    # -----------------------

    check_allowed_values(
        df,
        "Contract",
        {
            "Month-to-month",
            "One year",
            "Two year"
        }
    )

    # -----------------------
    # Minimum Rows
    # -----------------------

    check_row_count(
        df,
        7000
    )

    # -----------------------
    # Duplicate Customer IDs
    # -----------------------

    check_no_duplicates(
        df,
        "customerID"
    )

    # -----------------------
    # Warning Check
    # -----------------------

    check_churn_distribution(
        df,
        severity="WARNING"
    )

    # -----------------------
    # Create JSON Report
    # -----------------------

    write_quality_report()

    print(
        "\nPASS - All quality checks completed"
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    run_quality_checks()