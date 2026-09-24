"""
Loads trained scikit-learn models and runs inference.

Models are trained offline (see ml-notebooks/) and serialized with joblib
into app/ml/artifacts/. This module does NOT train anything -- it only
loads and predicts. Keeping training and serving separate means you can
retrain/swap a model without touching the API.

Expected artifact files (produced in Week 3-4, not present yet):
    app/ml/artifacts/diabetes_model.joblib
    app/ml/artifacts/heart_disease_model.joblib

Each artifact should be the full sklearn Pipeline (preprocessing + estimator)
so this module never has to reimplement scaling/encoding logic.
"""
import logging
import os
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

# Column order the model pipelines expect. This MUST match the training
# notebook's feature engineering exactly -- treat it as a contract between
# ml-notebooks/ and this file. Update both together.
FEATURE_ORDER = {
    "diabetes": [
        "age",
        "bmi",
        "glucose",
        "systolic_bp",
        "diastolic_bp",
        "cholesterol_total",
        "smoker",
        "physically_active",
        "family_history",
    ],
    "heart_disease": [
        "age",
        "sex",
        "bmi",
        "systolic_bp",
        "diastolic_bp",
        "cholesterol_total",
        "smoker",
        "physically_active",
        "family_history",
    ],
}

RISK_THRESHOLDS = {"low": 0.33, "moderate": 0.66}  # upper bounds; > 0.66 = high


class ModelNotAvailableError(RuntimeError):
    """Raised when a prediction is requested for a model that hasn't been trained yet."""


def _artifact_path(condition: str) -> str:
    return os.path.join(ARTIFACTS_DIR, f"{condition}_model.joblib")


@lru_cache(maxsize=4)
def load_model(condition: str):
    path = _artifact_path(condition)
    if not os.path.exists(path):
        raise ModelNotAvailableError(
            f"No trained model found for '{condition}' at {path}. "
            "Train it first (see ml-notebooks/02_model_training.ipynb) and "
            "save the pipeline there with joblib.dump()."
        )
    logger.info("Loading model for %s from %s", condition, path)
    return joblib.load(path)


def _to_feature_frame(condition: str, input_data: dict) -> pd.DataFrame:
    """Convert the validated questionnaire dict into the exact row shape the
    model pipeline expects, encoding booleans as 0/1 and sex as 0/1."""
    row = dict(input_data)
    row["smoker"] = int(bool(row.get("smoker", False)))
    row["physically_active"] = int(bool(row.get("physically_active", True)))
    row["family_history"] = int(bool(row.get("family_history", False)))
    if "sex" in row:
        row["sex"] = 1 if row["sex"] == "male" else 0

    columns = FEATURE_ORDER[condition]
    ordered = {col: row[col] for col in columns if col in row}
    missing = [col for col in columns if col not in row]
    if missing:
        raise ValueError(f"Missing required feature(s) for {condition} model: {missing}")

    return pd.DataFrame([ordered], columns=columns)


def risk_label_for(score: float) -> str:
    if score <= RISK_THRESHOLDS["low"]:
        return "low"
    if score <= RISK_THRESHOLDS["moderate"]:
        return "moderate"
    return "high"


def predict(condition: str, input_data: dict) -> dict:
    """
    Returns:
        {
            "risk_score": float,      # probability of positive class, 0-1
            "risk_label": str,        # "low" | "moderate" | "high"
            "feature_frame": pd.DataFrame,  # single-row frame (reused by the SHAP explainer)
        }
    """
    model = load_model(condition)
    frame = _to_feature_frame(condition, input_data)

    proba = model.predict_proba(frame)[0]
    # Convention: index 1 = positive class (has the condition / at risk)
    risk_score = float(np.round(proba[1], 4))

    return {
        "risk_score": risk_score,
        "risk_label": risk_label_for(risk_score),
        "feature_frame": frame,
    }
