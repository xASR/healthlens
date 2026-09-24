"""
Regression tests against the REAL trained diabetes model artifact.
Requires backend/app/ml/artifacts/diabetes_model.joblib to exist --
skipped automatically if it doesn't (e.g. a fresh clone before training).
"""
import os

import pytest

from app.ml.explainer import explain
from app.ml.predictor import ModelNotAvailableError, predict
from app.recommendations.engine import build_recommendations

ARTIFACT = os.path.join(
    os.path.dirname(__file__), "..", "app", "ml", "artifacts", "diabetes_model.joblib"
)
requires_model = pytest.mark.skipif(
    not os.path.exists(ARTIFACT), reason="diabetes_model.joblib not trained yet"
)

HIGH_RISK = {
    "age": 45, "sex": "female", "bmi": 31.2, "systolic_bp": 128, "diastolic_bp": 88,
    "glucose": 158, "cholesterol_total": 190, "pregnancies": 3,
    "smoker": False, "physically_active": False, "family_history": True,
}
LOW_RISK = dict(HIGH_RISK, glucose=88, bmi=22.0, age=24, pregnancies=0, family_history=False)


@requires_model
def test_predict_returns_valid_risk_score():
    result = predict("diabetes", HIGH_RISK)
    assert 0.0 <= result["risk_score"] <= 1.0
    assert result["risk_label"] in {"low", "moderate", "high"}


@requires_model
def test_model_direction_is_sane():
    """A clearly lower-risk profile must score lower than a clearly higher-risk one."""
    high = predict("diabetes", HIGH_RISK)
    low = predict("diabetes", LOW_RISK)
    assert low["risk_score"] < high["risk_score"]


@requires_model
def test_shap_explanation_returns_ranked_factors():
    result = predict("diabetes", HIGH_RISK)
    top_factors = explain("diabetes", result["feature_frame"])
    assert len(top_factors) == 4
    impacts = [abs(f["impact"]) for f in top_factors]
    assert impacts == sorted(impacts, reverse=True), "factors must be ranked by |impact|"
    assert all("feature" in f and "value" in f for f in top_factors)


@requires_model
def test_full_pipeline_end_to_end():
    """predict -> explain -> recommend, exactly as the API route calls it."""
    result = predict("diabetes", HIGH_RISK)
    top_factors = explain("diabetes", result["feature_frame"])
    rec = build_recommendations("diabetes", result["risk_label"], top_factors)
    assert len(rec["diet"]) >= 1
    assert len(rec["exercise"]) >= 1
    assert rec["specialist"]
    assert rec["urgency_note"]


def test_missing_model_raises_clean_error():
    # heart_disease is trained now too, so probe a condition that will
    # never have an artifact instead of hardcoding a model we expect to
    # eventually exist.
    with pytest.raises(ModelNotAvailableError):
        predict("nonexistent_condition", HIGH_RISK)
