"""
Automated Integration and Unit Tests for Churn Prediction API.

Tests API endpoints using FastAPI TestClient:
- Health check and documentation endpoints
- Web dashboard HTML static serving
- Model metrics and feature importance contracts
- Inference predictions on high-risk vs low-risk profiles
- Input validation boundaries and error status codes (422)
"""

import pytest
from fastapi.testclient import TestClient
from src.api import app


@pytest.fixture(scope="module")
def client():
    """
    TestClient fixture using lifespan context manager.
    Why: Entering the TestClient context triggers FastAPI's lifespan events,
    ensuring the trained model pipeline is loaded before running tests.
    """
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client: TestClient):
    """GET /health must return 200 OK and confirm model is loaded."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True


def test_api_welcome_endpoint(client: TestClient):
    """GET /api returns welcome message and link to docs."""
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert "documentation" in data
    assert data["documentation"] == "/docs"


def test_serve_dashboard_html(client: TestClient):
    """GET / must return 200 OK with HTML content."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "<!DOCTYPE html>" in response.text
    assert "ChurnGuard" in response.text


def test_metrics_endpoint(client: TestClient):
    """GET /api/metrics returns real metrics with expected structure and keys."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "dataset_size" in data
    assert "churn_rate" in data
    assert "random_forest" in data
    assert "logistic_regression" in data

    rf = data["random_forest"]
    for key in ["accuracy", "precision", "recall", "f1", "roc_auc", "confusion_matrix"]:
        assert key in rf
        assert rf[key] is not None


def test_feature_importance_endpoint(client: TestClient):
    """GET /api/feature-importance returns top features list."""
    response = client.get("/api/feature-importance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first_item = data[0]
    assert "feature" in first_item
    assert "importance" in first_item
    assert isinstance(first_item["importance"], float)


def test_predict_high_risk_customer(client: TestClient):
    """
    POST /predict for typical high-risk profile:
    Short tenure (2m), month-to-month contract, fiber optic, electronic check.
    Must return 200, valid probability, High risk level, and retention suggestions.
    """
    payload = {
        "tenure": 2,
        "monthly_charges": 85.5,
        "total_charges": 171.0,
        "contract": "Month-to-month",
        "internet_service": "Fiber optic",
        "payment_method": "Electronic check",
        "paperless_billing": "Yes",
        "tech_support": "No",
        "online_security": "No",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    result = response.json()

    assert "will_churn" in result
    assert "churn_probability" in result
    assert "risk_level" in result
    assert "suggestions" in result

    assert 0.0 <= result["churn_probability"] <= 1.0
    assert result["risk_level"] in ["Medium", "High"]
    assert len(result["suggestions"]) >= 2


def test_predict_risk_comparison(client: TestClient):
    """
    POST /predict must assign significantly lower churn probability
    to a loyal long-term customer (tenure 60m, 2-year contract)
    than to a volatile short-term customer (tenure 2m, month-to-month).
    """
    high_risk_payload = {
        "tenure": 2,
        "monthly_charges": 85.0,
        "total_charges": 170.0,
        "contract": "Month-to-month",
        "internet_service": "Fiber optic",
        "payment_method": "Electronic check",
        "paperless_billing": "Yes",
        "tech_support": "No",
        "online_security": "No",
    }
    low_risk_payload = {
        "tenure": 60,
        "monthly_charges": 45.0,
        "total_charges": 2700.0,
        "contract": "Two year",
        "internet_service": "DSL",
        "payment_method": "Credit card (automatic)",
        "paperless_billing": "No",
        "tech_support": "Yes",
        "online_security": "Yes",
    }

    res_high = client.post("/predict", json=high_risk_payload).json()
    res_low = client.post("/predict", json=low_risk_payload).json()

    assert res_high["churn_probability"] > res_low["churn_probability"]
    assert res_low["risk_level"] == "Low"


def test_predict_validation_invalid_contract(client: TestClient):
    """POST /predict with unrecognized contract string must return 422 Unprocessable Entity."""
    invalid_payload = {
        "tenure": 12,
        "monthly_charges": 50.0,
        "total_charges": 600.0,
        "contract": "Three year lifetime",  # Invalid
        "internet_service": "DSL",
        "payment_method": "Mailed check",
        "paperless_billing": "No",
        "tech_support": "Yes",
        "online_security": "Yes",
    }
    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422


def test_predict_validation_negative_tenure(client: TestClient):
    """POST /predict with negative tenure must return 422 Unprocessable Entity."""
    invalid_payload = {
        "tenure": -5,  # Invalid: ge=0 constraint
        "monthly_charges": 50.0,
        "total_charges": 600.0,
        "contract": "Month-to-month",
        "internet_service": "DSL",
        "payment_method": "Mailed check",
        "paperless_billing": "No",
        "tech_support": "Yes",
        "online_security": "Yes",
    }
    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422
