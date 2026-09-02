import datetime

from pydantic import BaseModel, ConfigDict, Field


class TopFactor(BaseModel):
    feature: str
    impact: float  # signed SHAP value; positive = increases risk
    value: float | str  # the user's actual input for that feature


class Recommendations(BaseModel):
    diet: list[str]
    exercise: list[str]
    specialist: str
    urgency_note: str


class PredictionResult(BaseModel):
    assessment_id: str
    condition: str
    risk_score: float
    risk_label: str
    top_factors: list[TopFactor]
    recommendations: Recommendations
    disclaimer: str = (
        "HealthLens is a preliminary screening tool, not a medical diagnosis. "
        "Please consult a qualified healthcare professional for evaluation."
    )


class AssessmentHistoryItem(BaseModel):
    # The Assessment DB model's primary key column is "id", not
    # "assessment_id" -- validation_alias tells pydantic to read from
    # obj.id when building this from an ORM object (response_model=
    # list[AssessmentHistoryItem] in routes_history.py), while keeping the
    # outward-facing JSON key as "assessment_id" to match what the
    # frontend (Dashboard.jsx) and the single-item /history/{id} route
    # both already use. Without this, FastAPI raises a
    # ResponseValidationError ("assessment_id: Field required") on every
    # call -- this was a real, previously-uncaught bug, not a config issue.
    assessment_id: str = Field(validation_alias="id")
    condition: str
    risk_score: float
    risk_label: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
