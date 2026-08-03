"""
Request schema for a single risk assessment submission.

Field ranges are loose clinical sanity bounds -- they stop garbage input
(negative age, BMI of 900) without pretending to be medical validation.
Adjust once you've finalized which columns your trained model actually uses.
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QuestionnaireInput(BaseModel):
    condition: Literal["diabetes", "heart_disease"] = "diabetes"

    age: int = Field(..., ge=1, le=120)
    sex: Literal["male", "female"]
    bmi: float = Field(..., ge=10, le=80)
    systolic_bp: int = Field(..., ge=70, le=250, description="mmHg")
    diastolic_bp: int = Field(..., ge=40, le=150, description="mmHg")
    glucose: float = Field(..., ge=40, le=500, description="mg/dL, fasting")
    cholesterol_total: float = Field(..., ge=100, le=400, description="mg/dL")

    # Lifestyle factors -- keep these as simple booleans/ordinal scales so
    # they map cleanly onto model features later.
    smoker: bool = False
    physically_active: bool = True
    family_history: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "condition": "diabetes",
                "age": 45,
                "sex": "female",
                "bmi": 27.5,
                "systolic_bp": 128,
                "diastolic_bp": 82,
                "glucose": 110,
                "cholesterol_total": 190,
                "smoker": False,
                "physically_active": True,
                "family_history": True,
            }
        }
    )
