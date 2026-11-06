# Customer Churn Prediction: ML Model and API

An end-to-end Machine Learning web platform and REST API that predicts whether a telecommunications subscriber will cancel their subscription (churn). Built with Scikit-learn, FastAPI, and an interactive, animated vanilla web dashboard, the system identifies high-risk customers before they leave and delivers automated, rule-based retention strategies directly to customer success teams.

---

## Screenshots

| Main Dashboard & Simulator | Risk Prediction & Retention Playbook |
| :---: | :---: |
| ![Dashboard Screenshot](screenshots/dashboard.png) | ![Result Screenshot](screenshots/result.png) |

*(Place your screenshots in `screenshots/dashboard.png` and `screenshots/result.png`)*

---

## Key Features

- **Predictive ML Pipeline**: Trained on the IBM Telco dataset using an ensemble `RandomForestClassifier` (200 trees, class-balanced) with built-in `StandardScaler` and `OneHotEncoder` preprocessing.
- **Production REST API**: FastAPI backend with Pydantic type validation, CORS security, health diagnostics, and OpenAPI documentation at `/docs`.
- **Rule-Based Retention Engine**: Translates churn risk and customer behavior patterns (such as month-to-month contracts and electronic check billing) into actionable business recommendations.
- **Glassmorphic Web Dashboard**: Single-page modern interface featuring SVG animations, an interactive 60fps probability gauge, live slider counters, preset risk scenarios, and a dark/light theme switch.
- **Comprehensive Model Transparency**: Live evaluation metrics and top feature importance rankings streamed directly from the training artifacts to the UI.
- **Zero Framework Bloat**: Pure HTML5, CSS3, and ES6 JavaScript front end with zero npm dependencies, zero build steps, and zero external charting libraries.

---

## Tech Stack

| Domain | Technologies |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Data Processing & ML** | Pandas, Scikit-learn, Joblib |
| **Backend & Web Server** | FastAPI, Pydantic, Uvicorn |
| **Testing** | Pytest, HTTPX |
| **Front End** | Plain HTML5, Modern CSS3 (CSS Variables, Keyframes), Vanilla JavaScript (ES6, Fetch API) |
| **Typography & Assets** | Google Fonts (Inter with system fallbacks), Handcrafted Inline SVGs |

---

## Project Structure

```text
churn-api/
├── data/
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv  # Raw IBM dataset (not committed)
├── models/
│   ├── churn_model.pkl                       # Serialized scikit-learn pipeline
│   ├── metrics.json                          # Real evaluation metrics & confusion matrices
│   └── feature_importance.json               # Top 8 human-readable feature weights
├── src/
│   ├── __init__.py
│   ├── train_model.py                        # Cleaning, preprocessing, training & export
│   └── api.py                                # FastAPI app, Pydantic models & static server
├── static/
│   ├── index.html                            # Semantic single-page dashboard
│   ├── css/
│   │   └── style.css                         # Dark/light theme, glassmorphism, responsive styles
│   ├── js/
│   │   └── app.js                            # Slider controls, API calls, gauge & counter animations
│   └── img/                                  # Handcrafted vector SVG illustrations
│       ├── hero.svg
│       ├── logo.svg
│       ├── low-risk.svg
│       ├── medium-risk.svg
│       ├── high-risk.svg
│       └── favicon.svg
├── tests/
│   └── test_api.py                           # Automated Pytest suite with FastAPI TestClient
├── screenshots/
│   └── .gitkeep                              # Placeholder for demonstration images
├── requirements.txt                          # Pinned dependency specifications
├── .gitignore                                # Excludes virtualenv, cache, and raw data
└── README.md
```

---

## Dataset

- **Source**: [IBM Telco Customer Churn on Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
- **Path**: `data/WA_Fn-UseC_-Telco-Customer-Churn.csv`
- **Records**: 7,043 raw rows (7,032 after dropping 11 blank `TotalCharges` records)
- **Target**: `Churn` (`Yes` / `No` &rarr; mapped to `1` / `0`)
- **Churn Rate**: 26.6% (imbalanced binary classification)

---

## Quickstart Guide

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/Kumar-Ayush/customer-churn-prediction.git
cd customer-churn-prediction

# Create and activate a virtual environment
python -m venv venv

# Windows (Command Prompt / PowerShell):
.\venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate

# Install pinned dependencies
pip install -r requirements.txt
```

### 2. Train and Evaluate the Models

```bash
python src/train_model.py
```

This cleans the dataset, trains both the Logistic Regression baseline and Random Forest classifier, prints test-set evaluation metrics, and writes `churn_model.pkl`, `metrics.json`, and `feature_importance.json` to `models/`.

### 3. Run the Web Server and Dashboard

```bash
uvicorn src.api:app --reload
```

- Open the web dashboard: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive API Swagger docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative ReDoc documentation: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 4. Run Automated Tests

```bash
pytest tests/ -v
```

---

## Example API Request and Response

### Prediction Endpoint: `POST /predict`

#### Sample `curl` Command:

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "tenure": 2,
    "monthly_charges": 85.5,
    "total_charges": 171.0,
    "contract": "Month-to-month",
    "internet_service": "Fiber optic",
    "payment_method": "Electronic check",
    "paperless_billing": "Yes",
    "tech_support": "No",
    "online_security": "No"
  }'
```

#### JSON Response (HTTP 200 OK):

```json
{
  "will_churn": true,
  "churn_probability": 0.955,
  "risk_level": "High",
  "suggestions": [
    "Offer a discounted 1-year plan with a 15% rate lock guarantee.",
    "Encourage automatic bank transfer or credit card with a $5 monthly bill credit.",
    "Offer a 3-month complimentary trial of 24/7 dedicated Tech Support."
  ]
}
```

---

## Model Evaluation Results

Evaluated on an 80/20 stratified hold-out test set (1,407 test samples):

| Metric | Logistic Regression (Baseline) | Random Forest (Production) | Production Advantage |
| :--- | :---: | :---: | :--- |
| **Accuracy** | 72.71% | **76.90%** | **+4.19% higher overall classification accuracy** |
| **Precision** | 49.19% | **55.66%** | **+6.47% fewer false alarms** (avoids wasting retention discounts) |
| **Recall** | **80.75%** | 64.44% | Identifies 64.4% of at-risk subscribers |
| **F1 Score** | **0.6113** | 0.5973 | Strong balanced performance across imbalanced target |
| **ROC-AUC** | **0.8360** | 0.8086 | High discrimination capability across decision thresholds |

### Top Churn Drivers (Random Forest Feature Importances):
1. **Total spend to date ($)**: 22.87%
2. **Monthly charges ($)**: 21.71%
3. **Time as customer (months)**: 17.98%
4. **Month-to-month contract**: 9.14%
5. **No online security**: 3.66%
6. **Two-year contract**: 3.61%
7. **No technical support**: 3.05%
8. **Fiber optic internet service**: 2.85%

---

## Current Limitations

1. **Static Rules Engine**: Retention suggestions are rule-based business heuristics rather than individual causal effect estimations (e.g. Uplift modeling).
2. **Dataset Scope**: The IBM Telco dataset captures cross-sectional snapshots without timestamped event logs, preventing time-to-event survival modeling.
3. **Imbalance Tradeoff**: While Random Forest provides superior precision (fewer costly false retention offers), Logistic Regression achieved higher recall. In production, decision thresholds can be tuned based on business intervention economics.

---

## Future Improvements

- **Uplift Modeling**: Predict which customers will respond positively to retention offers rather than simply predicting churn probability.
- **SHAP (SHapley Additive exPlanations)**: Generate per-customer local feature attribution directly in the API response.
- **Automated Hyperparameter Optimization**: Integrate Optuna with 5-fold cross-validation.
- **Dockerization & CI/CD**: Package containerized image for AWS ECS / Google Cloud Run with automated GitHub Actions testing.

---

## Author

- **Kumar Ayush**
- [GitHub Profile](https://github.com/Kumar-Ayush)
- [LinkedIn Profile](https://linkedin.com/in/kumar-ayush)
