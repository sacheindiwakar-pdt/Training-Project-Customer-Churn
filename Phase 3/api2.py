from sqlalchemy import text


def get_churn_summary(db):

    summary_query = text("""
        SELECT
            COUNT(*) AS total_customers,
            SUM(churn) AS total_churned,
            AVG(churn) AS churn_rate
        FROM fact_customer_account
    """)

    summary = db.execute(summary_query).fetchone()

    contract_query = text("""
        SELECT
            dc.contract_name AS contract_type,
            AVG(f.churn) AS churn_rate
        FROM fact_customer_account f
        JOIN dim_contract dc
            ON f.contract_key = dc.contract_key
        GROUP BY dc.contract_name
    """)

    contract_results = db.execute(contract_query).fetchall()

    internet_query = text("""
        SELECT
            s.InternetService AS internet_service,
            AVG(f.churn) AS churn_rate
        FROM fact_customer_account f
        JOIN stage_customer s
            ON f.customer_id = s.customerID
        GROUP BY s.InternetService
    """)

    internet_results = db.execute(internet_query).fetchall()

    return {
        "total_customers": summary.total_customers,
        "total_churned": summary.total_churned,
        "churn_rate": float(summary.churn_rate),

        "by_contract": [
            {
                "contract_type": row.contract_type,
                "churn_rate": float(row.churn_rate)
            }
            for row in contract_results
        ],

        "by_internet_service": [
            {
                "internet_service": row.internet_service,
                "churn_rate": float(row.churn_rate)
            }
            for row in internet_results
        ]
    }