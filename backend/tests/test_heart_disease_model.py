"""
Regression tests against the REAL trained heart disease model artifact.
Requires backend/app/ml/artifacts/heart_disease_model.joblib to exist --
skipped automatically if it doesn't (e.g. a fresh clone before training).
"""
import os

import pytest

from app.ml.explainer import explain
from app.ml.predictor import predict
from app.recommendations.engine import build_recommendations

ARTIFACT = os.path.join(
    os.path.dirname(__file__), "..", "app", "ml", "artifacts", "heart_disease_model.joblib"
)
requires_model = pytest.mark.skipif(
    not os.path.exists(ARTIFACT), reason="heart_disease_model.joblib not trained yet"
)

HIGH_RISK = {
    "age": 63, "sex": "male", "chest_pain_type": "asymptomatic",
    "systolic_bp": 160, "cholesterol_total": 286, "glucose": 145,
    "exercise_angina": True,
    # not used by the heart disease model itself, but required by the shared schema
    "bmi": 29.0, "diastolic_bp": 90,
    "smoker": True, "physically_active": False, "family_history": True,
}
LOW_RISK = dict(
    HIGH_RISK,
    age=35, chest_pain_type="typical_angina", systolic_bp=112,
    cholesterol_total=175, glucose=88, exercise_angina=False,
    smoker=False, physically_active=True,
)


@requires_model
def test_predict_returns_valid_risk_score():
    result = predict("heart_disease", HIGH_RISK)
    assert 0.0 <= result["risk_score"] <= 1.0
    assert result["risk_label"] in {"low", "moderate", "high"}


@requires_model
def test_model_direction_is_sane():
    """A clearly lower-risk profile must score lower than a clearly higher-risk one."""
    high = predict("heart_disease", HIGH_RISK)
    low = predict("heart_disease", LOW_RISK)
    assert low["risk_score"] < high["risk_score"]


@requires_model
def test_missing_chest_pain_type_raises_clean_error():
    """chest_pain_type has no safe default -- it must be explicitly provided."""
    incomplete = dict(HIGH_RISK)
    incomplete.pop("chest_pain_type")
    with pytest.raises(ValueError, match="chest_pain_type"):
        predict("heart_disease", incomplete)


@requires_model
def test_fbs_derived_from_glucose():
    """fbs isn't asked directly -- it's derived from the glucose field per the >120 mg/dL rule."""
    result = predict("heart_disease", dict(HIGH_RISK, glucose=200))
    assert result["feature_frame"].iloc[0]["fbs"] == 1
    result = predict("heart_disease", dict(HIGH_RISK, glucose=90))
    assert result["feature_frame"].iloc[0]["fbs"] == 0


@requires_model
def test_shap_explanation_returns_ranked_factors():
    result = predict("heart_disease", HIGH_RISK)
    top_factors = explain("heart_disease", result["feature_frame"])
    assert len(top_factors) == 4
    impacts = [abs(f["impact"]) for f in top_factors]
    assert impacts == sorted(impacts, reverse=True), "factors must be ranked by |impact|"
    assert all("feature" in f and "value" in f for f in top_factors)


@requires_model
def test_full_pipeline_end_to_end():
    """predict -> explain -> recommend, exactly as the API route calls it."""
    result = predict("heart_disease", HIGH_RISK)
    top_factors = explain("heart_disease", result["feature_frame"])
    rec = build_recommendations("heart_disease", result["risk_label"], top_factors)
    assert len(rec["diet"]) >= 1
    assert len(rec["exercise"]) >= 1
    assert rec["specialist"]
    assert rec["urgency_note"]
