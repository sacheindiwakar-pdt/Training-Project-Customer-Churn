from sqlalchemy import text
from fastapi import HTTPException


def get_customer_features(db, customer_id):

    query = text("""
        SELECT
            service_count,
            tenure_bucket,
            high_charge_flag,
            is_long_term_customer,
            has_streaming_bundle,
            auto_pay_flag,
            monthly_charges,
            total_charges
        FROM customer_ml_features
        WHERE customer_id = :customer_id
    """)

    result = db.execute(
        query,
        {"customer_id": customer_id}
    ).fetchone()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Customer '{customer_id}' not found"
        )

    return {
        "service_count": result.service_count,
        "tenure_bucket": result.tenure_bucket,
        "high_charge_flag": result.high_charge_flag,
        "is_long_term_customer": result.is_long_term_customer,
        "has_streaming_bundle": result.has_streaming_bundle,
        "auto_pay_flag": result.auto_pay_flag,
        "monthly_charges": result.monthly_charges,
        "total_charges": result.total_charges
    }