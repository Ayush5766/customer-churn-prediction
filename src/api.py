"""
FastAPI REST API and Web Server for Customer Churn Prediction.

Provides prediction endpoints, model performance metrics, feature importance data,
and serves the interactive front-end dashboard.
"""

from contextlib import asynccontextmanager
import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Project directory paths
ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"
MODEL_PATH = MODELS_DIR / "churn_model.pkl"
METRICS_PATH = MODELS_DIR / "metrics.json"
FEATURE_IMPORTANCE_PATH = MODELS_DIR / "feature_importance.json"
STATIC_DIR = ROOT_DIR / "static"

# Global model container (loaded once at startup for high throughput)
ml_artifacts: Dict[str, Any] = {
    "pipeline": None,
    "metrics": None,
    "feature_importance": None,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Loads the trained model pipeline and cached JSON metrics when the server starts.
    Why: Loading once at startup avoids re-reading disk artifacts on every single HTTP request.
    """
    if MODEL_PATH.exists():
        try:
            ml_artifacts["pipeline"] = joblib.load(MODEL_PATH)
            print(f"Loaded production model from {MODEL_PATH}")
        except Exception as exc:
            print(f"Error loading model pipeline: {exc}")
    else:
        print(f"Warning: Model file not found at {MODEL_PATH}. Run src/train_model.py first.")

    if METRICS_PATH.exists():
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            ml_artifacts["metrics"] = json.load(f)

    if FEATURE_IMPORTANCE_PATH.exists():
        with open(FEATURE_IMPORTANCE_PATH, "r", encoding="utf-8") as f:
            ml_artifacts["feature_importance"] = json.load(f)

    yield

    # Clean shutdown if needed
    ml_artifacts.clear()


app = FastAPI(
    title="Customer Churn Prediction API",
    description="Production-grade ML API to predict customer churn probability and recommend retention strategies.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration: allows cross-origin requests for public API and cloud deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Pydantic Schemas for Request Validation and Response Contracts
# -----------------------------------------------------------------------------
class CustomerData(BaseModel):
    """
    Input schema validating raw customer attributes.
    Pydantic strictly enforces type checks and boundary limits before data reaches the model.
    """
    tenure: int = Field(
        ...,
        ge=0,
        le=100,
        description="Number of months customer has stayed with the company (0-100).",
        examples=[12],
    )
    monthly_charges: float = Field(
        ...,
        ge=0.0,
        description="Monthly service charge amount in INR (₹) (>= 0).",
        examples=[65.5],
    )
    total_charges: float = Field(
        ...,
        ge=0.0,
        description="Total cumulative amount charged to customer in INR (₹) (>= 0).",
        examples=[786.0],
    )
    contract: Literal["Month-to-month", "One year", "Two year"] = Field(
        ...,
        description="Contract commitment type.",
        examples=["Month-to-month"],
    )
    internet_service: Literal["DSL", "Fiber optic", "No"] = Field(
        ...,
        description="Type of internet service subscribed.",
        examples=["Fiber optic"],
    )
    payment_method: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ] = Field(
        ...,
        description="Billing payment method used by customer.",
        examples=["Electronic check"],
    )
    paperless_billing: Literal["Yes", "No"] = Field(
        ...,
        description="Whether paperless billing is enabled.",
        examples=["Yes"],
    )
    tech_support: Literal["Yes", "No", "No internet service"] = Field(
        ...,
        description="Whether technical support add-on is active.",
        examples=["No"],
    )
    online_security: Literal["Yes", "No", "No internet service"] = Field(
        ...,
        description="Whether online security add-on is active.",
        examples=["No"],
    )


class PredictionResponse(BaseModel):
    """
    Prediction result output schema.
    """
    will_churn: bool = Field(..., description="Binary classification (True = likely to churn).")
    churn_probability: float = Field(
        ..., description="Predicted churn probability between 0.0 and 1.0 (3 decimals)."
    )
    risk_level: Literal["Low", "Medium", "High"] = Field(
        ..., description="Risk tier: Low (< 0.3), Medium (0.3 - 0.6), High (> 0.6)."
    )
    suggestions: List[str] = Field(
        ..., description="Rule-based retention action recommendations (2-3 items)."
    )


# -----------------------------------------------------------------------------
# Business Logic: Rule-based Retention Recommendations
# -----------------------------------------------------------------------------
def generate_retention_suggestions(data: CustomerData, probability: float) -> List[str]:
    """
    Generate proactive customer retention tips based on input risk factors.

    NOTE FOR CODE REVIEW / INTERVIEWS:
    These suggestions are deterministic, rule-based business heuristics derived from
    domain knowledge and exploratory data analysis. They are NOT direct outputs from the
    ML model's internal weights, but rather actionable advice triggered by specific input features.
    """
    tips: List[str] = []

    # High-churn driver: Month-to-month contracts have highest cancellation rates
    if data.contract == "Month-to-month":
        tips.append("Offer a discounted 1-year plan with a 15% rate lock guarantee.")

    # High-churn driver: Electronic checks have highest churn among payment methods
    if data.payment_method == "Electronic check":
        tips.append("Encourage automatic bank transfer or UPI/card payments with a ₹500 monthly bill discount.")

    # Internet customers lacking support or security leave significantly faster
    if data.tech_support == "No" and data.internet_service != "No":
        tips.append("Offer a 3-month complimentary trial of 24/7 dedicated Tech Support.")

    if data.online_security == "No" and data.internet_service != "No":
        tips.append("Recommend our Cyber Defense & Online Security package bundle.")

    # Critical early tenure window (first 6 months has steepest drop-off)
    if data.tenure <= 6:
        tips.append("Trigger a personalized customer success onboarding call and welcome bundle.")

    # High spenders feel price fatigue without perceived value
    if data.monthly_charges > 80.0 and len(tips) < 3:
        tips.append("Conduct an account service review to optimize plan features and cost.")

    # If customer is already low risk and loyal, focus on loyalty rewards
    if not tips:
        tips.append("Enroll customer in the VIP Loyalty Tier with exclusive partner perks.")
        tips.append("Send an annual appreciation gift or speed upgrade offer.")

    # Return top 2 to 3 suggestions
    return tips[:3]


# -----------------------------------------------------------------------------
# REST API Endpoints
# -----------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def serve_dashboard():
    """Serve the single-page HTML5 web dashboard."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard frontend file not found.",
        )
    return FileResponse(index_file)


@app.get("/api")
async def api_root():
    """API root providing welcome message and documentation link."""
    return {
        "message": "Welcome to the Customer Churn Prediction REST API",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "metrics": "/api/metrics",
            "feature_importance": "/api/feature-importance",
        },
    }


@app.get("/health")
async def health_check():
    """
    System health check returning model availability status.
    """
    model_loaded = ml_artifacts.get("pipeline") is not None
    return {
        "status": "ok",
        "model_loaded": model_loaded,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_churn(customer: CustomerData):
    """
    Predict customer churn probability and return retention suggestions.

    Takes validated customer attributes, passes them through the scikit-learn
    preprocessing + classification pipeline, and returns the risk level and rules.
    """
    pipeline = ml_artifacts.get("pipeline")
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Train the model using src/train_model.py before predicting.",
        )

    # Convert snake_case Pydantic attributes to exact training DataFrame column names
    input_row = pd.DataFrame(
        [
            {
                "tenure": customer.tenure,
                "MonthlyCharges": customer.monthly_charges,
                "TotalCharges": customer.total_charges,
                "Contract": customer.contract,
                "InternetService": customer.internet_service,
                "PaymentMethod": customer.payment_method,
                "PaperlessBilling": customer.paperless_billing,
                "TechSupport": customer.tech_support,
                "OnlineSecurity": customer.online_security,
            }
        ]
    )

    try:
        # Run inference through the full pipeline (scaling + one-hot + Random Forest)
        proba = pipeline.predict_proba(input_row)[0]
        churn_prob = round(float(proba[1]), 3)
        prediction = bool(pipeline.predict(input_row)[0] == 1)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failed: {str(exc)}",
        )

    # Assign risk tier based on calibrated probability boundaries
    if churn_prob < 0.3:
        risk_level = "Low"
    elif churn_prob <= 0.6:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # Generate rule-based recommendations for customer retention
    suggestions = generate_retention_suggestions(customer, churn_prob)

    return PredictionResponse(
        will_churn=prediction,
        churn_probability=churn_prob,
        risk_level=risk_level,
        suggestions=suggestions,
    )


@app.get("/api/metrics")
async def get_metrics():
    """Return trained model performance metrics (accuracy, precision, recall, F1, ROC-AUC)."""
    metrics = ml_artifacts.get("metrics")
    if metrics is None:
        if METRICS_PATH.exists():
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                metrics = json.load(f)
                ml_artifacts["metrics"] = metrics
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Metrics file not found. Run model training first.",
            )
    return metrics


@app.get("/api/feature-importance")
async def get_feature_importance():
    """Return top feature importance drivers for Random Forest."""
    features = ml_artifacts.get("feature_importance")
    if features is None:
        if FEATURE_IMPORTANCE_PATH.exists():
            with open(FEATURE_IMPORTANCE_PATH, "r", encoding="utf-8") as f:
                features = json.load(f)
                ml_artifacts["feature_importance"] = features
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feature importance file not found. Run model training first.",
            )
    return features


# Mount static assets directory for CSS, JS, and SVG images
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
