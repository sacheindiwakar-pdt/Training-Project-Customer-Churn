from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Header
)

from pydantic import (
    BaseModel,
    field_validator
)

from sqlalchemy import (
    create_engine,
    text
)

from sqlalchemy.orm import sessionmaker

from typing import Optional

from fastapi.middleware.cors import CORSMiddleware

from api2 import get_churn_summary
from api3 import get_high_risk_customers
from api4 import get_customer_features

from ml4 import (
    predict_churn as model_predict_churn
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# -------------------------------------------------
# API KEY
# -------------------------------------------------

API_KEY = "my-secret-key"


def verify_api_key(
    x_api_key: str = Header(None)
):

    if x_api_key != API_KEY:

        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

    return x_api_key


# -------------------------------------------------
# DATABASE
# -------------------------------------------------

DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/friday"
)

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -------------------------------------------------
# RESPONSE MODELS
# -------------------------------------------------

class CustomerResponse(BaseModel):

    customer_id: str
    tenure: int
    contract_type: str
    internet_service: str
    monthly_charges: float
    churn: int


class HighRiskCustomerResponse(BaseModel):

    customer_id: str
    tenure: int
    monthly_charges: float
    contract_type: str
    risk_reason: str


class CustomerFeaturesResponse(BaseModel):

    service_count: int
    tenure_bucket: str
    high_charge_flag: int
    is_long_term_customer: int
    has_streaming_bundle: int
    auto_pay_flag: int
    monthly_charges: float
    total_charges: float | None


# -------------------------------------------------
# PREDICTION REQUEST
# -------------------------------------------------

class ChurnPredictionRequest(
    BaseModel
):

    tenure: int
    monthly_charges: float
    contract_type: str
    internet_service: str
    service_count: int
    

    @field_validator(
        "tenure"
    )
    @classmethod
    def validate_tenure(
        cls,
        value
    ):

        if value < 0:

            raise ValueError(
                "tenure must be >= 0"
            )

        if value > 100:

            raise ValueError(
                "tenure must be <= 100"
            )

        return value

    @field_validator(
        "monthly_charges"
    )
    @classmethod
    def validate_monthly_charges(
        cls,
        value
    ):

        if value <= 0:

            raise ValueError(
                "monthly_charges must be > 0"
            )

        return value
    @field_validator("internet_service")
    @classmethod    
    def validate_internet_service(cls, value):

        allowed = [
        "DSL",
        "Fiber optic",
        "No"
        ]

        if value not in allowed:
            raise ValueError(
                "Invalid internet_service"
            )

        return value


# -------------------------------------------------
# ROUTES
# -------------------------------------------------

@app.get("/")
def root():

    return {
        "message":
        "Customer Churn API Running"
    }


@app.get("/churn/summary")
def churn_summary(
    api_key: str = Depends(
        verify_api_key
    )
):

    session = SessionLocal()

    try:

        return get_churn_summary(
            session
        )

    finally:

        session.close()


@app.get(
    "/customers/high-risk",
    response_model=list[
        HighRiskCustomerResponse
    ]
)
def high_risk_customers_route(
    limit: int = 50,
    min_tenure: Optional[int] = None,
    max_tenure: Optional[int] = None,
    api_key: str = Depends(
        verify_api_key
    )
):

    session = SessionLocal()

    try:

        return get_high_risk_customers(
            session,
            limit,
            min_tenure,
            max_tenure
        )

    finally:

        session.close()


@app.get(
    "/customer/{customer_id}/features",
    response_model=CustomerFeaturesResponse
)
def customer_features_route(
    customer_id: str,
    api_key: str = Depends(
        verify_api_key
    )
):

    session = SessionLocal()

    try:

        return get_customer_features(
            session,
            customer_id
        )

    finally:

        session.close()


@app.post("/predict-churn")
def predict_customer_churn(
    request: ChurnPredictionRequest,
    api_key: str = Depends(
        verify_api_key
    )
):

    result = model_predict_churn(
        tenure=request.tenure,
        monthly_charges=request.monthly_charges,
        contract_type=request.contract_type,
        internet_service=request.internet_service,
        service_count=request.service_count
        
    )

    return result