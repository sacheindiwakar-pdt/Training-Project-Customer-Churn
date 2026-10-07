import joblib
import pandas as pd

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

MODEL_PATH = "models/tree_churn.pkl"

FEATURE_PATH = "models/feature_columns.pkl"

model = joblib.load(MODEL_PATH)

FEATURE_COLUMNS = joblib.load(FEATURE_PATH)

# --------------------------------------------------
# PREPROCESS INPUT
# --------------------------------------------------

def preprocess_input(
    tenure,
    monthly_charges,
    contract_type,
    internet_service,
    service_count
):

    row = {
        col: 0
        for col in FEATURE_COLUMNS
    }

    if "tenure" in row:
        row["tenure"] = tenure

    if "monthly_charges" in row:
        row["monthly_charges"] = monthly_charges

    if "service_count" in row:
        row["service_count"] = service_count

    if "total_charges" in row:
        row["total_charges"] = (
            tenure * monthly_charges
        )

    if "high_charge_flag" in row:
        row["high_charge_flag"] = (
            1 if monthly_charges > 70 else 0
        )

    if "is_long_term_customer" in row:
        row["is_long_term_customer"] = (
            1 if tenure >= 24 else 0
        )

    if "has_streaming_bundle" in row:
        row["has_streaming_bundle"] = 0

    if "auto_pay_flag" in row:
        row["auto_pay_flag"] = 0

    contract_col = (
        f"contract_type_{contract_type}"
    )

    if contract_col in row:
        row[contract_col] = 1

    internet_col = (
    f"internet_service_{internet_service}"
)

    if internet_col in row:
        row[internet_col] = 1

    return pd.DataFrame(
        [row],
        columns=FEATURE_COLUMNS
    )

# --------------------------------------------------
# PREDICTION
# --------------------------------------------------

def predict_churn(
    tenure,
    monthly_charges,
    contract_type,
    internet_service,
    service_count
):

    X = preprocess_input(
        tenure,
        monthly_charges,
        contract_type,
        internet_service,
        service_count
    )

    prediction = model.predict(X)[0]

    probability = model.predict_proba(X)[0][1]

    return {

        "risk_score":
        round(
            float(probability),
            4
        ),

        "prediction":
        (
            "Likely to churn"
            if prediction == 1
            else "Unlikely to churn"
        ),

        "confidence":
        round(
            float(
                max(
                    probability,
                    1 - probability
                )
            ),
            4
        )
    }