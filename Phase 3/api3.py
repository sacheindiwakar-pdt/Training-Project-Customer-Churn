from sqlalchemy import text


def get_high_risk_customers(
    db,
    limit=50,
    min_tenure=None,
    max_tenure=None
):
    query = """
        SELECT
            customer_id,
            tenure,
            monthly_charges,
            contract_type,
            risk_reason
        FROM v_high_risk_customers
        WHERE 1=1
    """

    params = {}

    if min_tenure is not None:
        query += " AND tenure >= :min_tenure"
        params["min_tenure"] = min_tenure

    if max_tenure is not None:
        query += " AND tenure <= :max_tenure"
        params["max_tenure"] = max_tenure

    query += " LIMIT :limit"
    params["limit"] = limit

    result = db.execute(
        text(query),
        params
    ).fetchall()

    return [
        {
            "customer_id": row.customer_id,
            "tenure": row.tenure,
            "monthly_charges": row.monthly_charges,
            "contract_type": row.contract_type,
            "risk_reason": row.risk_reason
        }
        for row in result
    ]