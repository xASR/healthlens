import datetime

from pydantic import BaseModel, ConfigDict


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
    assessment_id: str
    condition: str
    risk_score: float
    risk_label: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
