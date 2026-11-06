"""
Model Training Script for Customer Churn Prediction.

Trains a Random Forest classifier and a Logistic Regression baseline,
evaluates both models on a stratified test set, and exports the production
pipeline, evaluation metrics, and feature importance rankings.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Define features used for training and prediction
NUMERIC_FEATURES: List[str] = ["tenure", "MonthlyCharges", "TotalCharges"]
CATEGORICAL_FEATURES: List[str] = [
    "Contract",
    "InternetService",
    "PaymentMethod",
    "PaperlessBilling",
    "TechSupport",
    "OnlineSecurity",
]

# Mapping technical feature names to clear plain-English labels for recruiters & business users
HUMAN_FEATURE_NAMES: Dict[str, str] = {
    "tenure": "Time as customer (months)",
    "MonthlyCharges": "Monthly charges (₹)",
    "TotalCharges": "Total spend to date (₹)",
    "Contract_Month-to-month": "Month-to-month contract",
    "Contract_One year": "One-year contract",
    "Contract_Two year": "Two-year contract",
    "InternetService_Fiber optic": "Fiber optic internet service",
    "InternetService_DSL": "DSL internet service",
    "InternetService_No": "No internet service",
    "PaymentMethod_Electronic check": "Electronic check payment",
    "PaymentMethod_Mailed check": "Mailed check payment",
    "PaymentMethod_Bank transfer (automatic)": "Automatic bank transfer",
    "PaymentMethod_Credit card (automatic)": "Automatic credit card",
    "PaperlessBilling_Yes": "Paperless billing active",
    "PaperlessBilling_No": "Paper billing active",
    "TechSupport_No": "No technical support",
    "TechSupport_Yes": "Technical support included",
    "TechSupport_No internet service": "No internet (tech support)",
    "OnlineSecurity_No": "No online security",
    "OnlineSecurity_Yes": "Online security included",
    "OnlineSecurity_No internet service": "No internet (online security)",
}


def load_and_clean_data(csv_path: Path) -> pd.DataFrame:
    """
    Load dataset from CSV, clean missing values, drop identifiers, and encode target.

    Why this matters:
    In the raw IBM dataset, TotalCharges contains blank spaces for new customers (tenure = 0).
    Converting them to numeric coercing errors to NaN lets us drop uninformative rows cleanly.
    """
    print(f"Loading raw data from: {csv_path}")
    df = pd.read_csv(csv_path)
    initial_rows = len(df)

    # Convert TotalCharges to float; blank strings become NaN
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].astype(str).str.strip(), errors="coerce")
    
    # Drop rows where TotalCharges is missing
    df = df.dropna(subset=["TotalCharges"]).copy()
    dropped_count = initial_rows - len(df)
    print(f"Data cleaning: dropped {dropped_count} rows with missing TotalCharges ({initial_rows} -> {len(df)})")

    # Drop non-predictive unique ID
    if "customerID" in df.columns:
        df = df.drop(columns=["customerID"])

    # Encode binary target: Yes = 1 (churned), No = 0 (retained)
    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})
    return df


def build_preprocessor() -> ColumnTransformer:
    """
    Construct preprocessing pipeline for numeric and categorical features.

    Why ColumnTransformer:
    It bundles scaling for continuous variables and one-hot encoding for nominal categories
    into a single transformer that can be embedded into the model pipeline.
    This prevents data leakage and ensures incoming raw JSON from the API is transformed automatically.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ],
        verbose_feature_names_out=False,
    )
    return preprocessor


def evaluate_model(model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
    """
    Compute accuracy, precision, recall, F1, ROC-AUC, and confusion matrix.

    Why multiple metrics:
    Customer churn datasets have class imbalance (~26% churn).
    Accuracy alone can be misleading; Recall measures how many actual churners we catch,
    and ROC-AUC measures discrimination capability across thresholds.
    """
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    cm = confusion_matrix(y_test, y_pred).tolist()

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "f1": round(float(f1_score(y_test, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "confusion_matrix": cm,
    }
    return metrics


def extract_feature_importance(pipeline: Pipeline, top_n: int = 8) -> List[Dict[str, Any]]:
    """
    Extract feature importances from Random Forest and map to plain-English labels.
    """
    preprocessor = pipeline.named_steps["preprocessor"]
    rf = pipeline.named_steps["classifier"]

    feature_names = preprocessor.get_feature_names_out()
    importances = rf.feature_importances_

    ranked: List[Dict[str, Any]] = []
    for name, imp in zip(feature_names, importances):
        # Translate to human label or fallback to formatted raw name
        human_name = HUMAN_FEATURE_NAMES.get(name, name.replace("_", " "))
        ranked.append({"feature": human_name, "importance": round(float(imp), 4)})

    # Sort descending by importance score and take top N
    ranked.sort(key=lambda item: item["importance"], reverse=True)
    return ranked[:top_n]


def train() -> Tuple[Pipeline, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Main training workflow:
    1. Load and clean dataset
    2. Split train/test (80/20 stratified)
    3. Train Logistic Regression baseline and Random Forest classifier
    4. Compare metrics and print results
    5. Save model artifact, metrics.json, and feature_importance.json
    """
    root_dir = Path(__file__).resolve().parent.parent
    data_path = root_dir / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
    models_dir = root_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    df = load_and_clean_data(data_path)

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df["Churn"]

    dataset_size = len(df)
    churn_rate = round(float(y.mean()), 4)
    print(f"Total dataset size: {dataset_size} rows | Overall churn rate: {churn_rate * 100:.1f}%")

    # Stratified 80/20 train/test split to preserve churn ratio in both sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train set: {len(X_train)} samples | Test set: {len(X_test)} samples\n")

    # 1. Train Logistic Regression baseline (class_weight='balanced' to handle churn imbalance)
    print("Training Baseline: Logistic Regression...")
    preprocessor_lr = build_preprocessor()
    lr_pipeline = Pipeline(
        [
            ("preprocessor", preprocessor_lr),
            (
                "classifier",
                LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42),
            ),
        ]
    )
    lr_pipeline.fit(X_train, y_train)
    lr_metrics = evaluate_model(lr_pipeline, X_test, y_test)

    # 2. Train Random Forest Classifier
    print("Training Production Model: Random Forest Classifier (200 trees)...")
    preprocessor_rf = build_preprocessor()
    rf_pipeline = Pipeline(
        [
            ("preprocessor", preprocessor_rf),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200, random_state=42, class_weight="balanced"
                ),
            ),
        ]
    )
    rf_pipeline.fit(X_train, y_train)
    rf_metrics = evaluate_model(rf_pipeline, X_test, y_test)

    # Print comparison
    print("\n" + "=" * 55)
    print("MODEL COMPARISON (Stratified Test Set - 1,407 rows)")
    print("=" * 55)
    print(f"{'Metric':<18}{'Logistic Regression':<22}{'Random Forest'}")
    print("-" * 55)
    for m in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
        print(f"{m.upper():<18}{lr_metrics[m]:<22.4f}{rf_metrics[m]:.4f}")
    print("-" * 55)
    print(f"LR Confusion Matrix (TN, FP / FN, TP):\n  {lr_metrics['confusion_matrix']}")
    print(f"RF Confusion Matrix (TN, FP / FN, TP):\n  {rf_metrics['confusion_matrix']}")
    print("=" * 55 + "\n")

    # Extract top feature importances from Random Forest
    top_features = extract_feature_importance(rf_pipeline, top_n=8)
    print("Top Feature Drivers of Churn (Random Forest):")
    for idx, item in enumerate(top_features, 1):
        print(f"  {idx}. {item['feature']:<35} {item['importance'] * 100:.2f}%")

    # Save artifacts
    model_path = models_dir / "churn_model.pkl"
    joblib.dump(rf_pipeline, model_path)
    print(f"\nSaved production pipeline to: {model_path}")

    all_metrics = {
        "dataset_size": dataset_size,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "churn_rate": churn_rate,
        "random_forest": rf_metrics,
        "logistic_regression": lr_metrics,
    }

    metrics_path = models_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"Saved metrics to: {metrics_path}")

    features_path = models_dir / "feature_importance.json"
    with open(features_path, "w", encoding="utf-8") as f:
        json.dump(top_features, f, indent=2)
    print(f"Saved feature importance to: {features_path}\n")

    return rf_pipeline, all_metrics, top_features


if __name__ == "__main__":
    train()
