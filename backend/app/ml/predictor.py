"""
Loads trained scikit-learn models and runs inference.

Models are trained offline (see ml-notebooks/) and serialized with joblib
into app/ml/artifacts/. This module does NOT train anything -- it only
loads and predicts. Keeping training and serving separate means you can
retrain/swap a model without touching the API.

Artifact contract: we save the RAW tree estimator (RandomForestClassifier
or XGBClassifier), not wrapped in a sklearn Pipeline. Two reasons: tree
models need no feature scaling, and shap.TreeExplainer (see explainer.py)
requires the raw estimator directly -- it cannot introspect through a
Pipeline wrapper. If a future model needs preprocessing (e.g. a logistic
regression baseline), that preprocessing must happen in _to_feature_frame
below, not inside the saved artifact.
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
# script's feature engineering exactly -- treat it as a contract between
# ml-notebooks/ and this file. Update both together.
#
# Diabetes model is trained on the Pima Indians Diabetes Dataset, which
# covers only female patients 21+. "pregnancies" is asked only for female
# users in the questionnaire and defaults to 0 for male users -- a
# documented dataset limitation, not an oversight (see ml-notebooks/README.md).
#
# Heart disease model is trained on the UCI Heart Disease (Cleveland)
# dataset, restricted to columns a self-screening user can actually
# report: age, sex, chest pain type, resting BP, cholesterol, fasting
# blood sugar, and exercise-induced chest pain. Excludes restecg,
# thalach, oldpeak, slope, ca, thal -- all outputs of a cardiac workup
# (stress-test ECG, fluoroscopy, thallium scan) that a screening tool's
# whole purpose is to tell someone whether they need. See
# ml-notebooks/README.md for the full rationale and the accuracy
# tradeoff this costs. "fbs" is not asked directly -- see
# _to_feature_frame below, it's derived from the "glucose" field already
# collected for the diabetes model.
FEATURE_ORDER = {
    "diabetes": ["pregnancies", "glucose", "diastolic_bp", "bmi", "age"],
    "heart_disease": [
        "age",
        "sex",
        "chest_pain_type",
        "systolic_bp",
        "cholesterol_total",
        "fbs",
        "exercise_angina",
    ],
}

# UCI Cleveland "cp" column encoding -- must match ml-notebooks/train_heart_disease_model.py
CHEST_PAIN_TYPE_MAP = {
    "typical_angina": 1,
    "atypical_angina": 2,
    "non_anginal_pain": 3,
    "asymptomatic": 4,
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
            f"Train it first (see ml-notebooks/{condition}_model_training.ipynb) "
            "and save the pipeline there with joblib.dump()."
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
    # Diabetes model trained on the Pima dataset (female patients only).
    # "pregnancies" is only collected from female users in the frontend;
    # male users implicitly get 0. This is a documented dataset limitation
    # (see ml-notebooks/README.md), not silent data fabrication.
    if condition == "diabetes":
        row.setdefault("pregnancies", 0)

    # Heart disease model: chest_pain_type is a required categorical input
    # (no sane default -- unlike pregnancies/smoker, guessing a chest-pain
    # status would fabricate a clinical answer). fbs is derived from the
    # fasting glucose value already collected, rather than asked as a
    # separate question -- see FEATURE_ORDER comment above.
    if condition == "heart_disease":
        cp = row.get("chest_pain_type")
        if cp not in CHEST_PAIN_TYPE_MAP:
            raise ValueError(
                "chest_pain_type is required for heart_disease and must be "
                f"one of: {', '.join(CHEST_PAIN_TYPE_MAP)}"
            )
        row["chest_pain_type"] = CHEST_PAIN_TYPE_MAP[cp]
        row["exercise_angina"] = int(bool(row.get("exercise_angina", False)))
        row["fbs"] = 1 if float(row.get("glucose", 0)) > 120 else 0

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
