import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_db_user
from app.db.database import get_db
from app.db.models import Assessment, User
from app.ml.explainer import explain
from app.ml.predictor import ModelNotAvailableError, predict
from app.recommendations.engine import build_recommendations
from app.schemas.prediction import PredictionResult
from app.schemas.questionnaire import QuestionnaireInput

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=PredictionResult, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: QuestionnaireInput,
    current_user: User = Depends(get_current_db_user),
    db: Session = Depends(get_db),
):
    """
    The core pipeline: questionnaire -> model prediction -> SHAP explanation
    -> rule-based recommendations -> persisted history row.
    """
    input_dict = payload.model_dump()

    try:
        prediction = predict(payload.condition, input_dict)
        top_factors = explain(payload.condition, prediction["feature_frame"])
    except ModelNotAvailableError as exc:
        # Expected until Week 3-4 model training is complete -- surfaced as
        # a clean 503 rather than a stack trace.
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except ValueError as exc:
        # e.g. chest_pain_type omitted for a heart_disease request -- it's
        # optional in the shared schema (see schemas/questionnaire.py) but
        # required per-condition, so that check happens here, not at the
        # pydantic layer. Surfaced as a clean 422, not a 500.
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    recommendations = build_recommendations(
        payload.condition, prediction["risk_label"], top_factors
    )

    record = Assessment(
        user_id=current_user.id,
        condition=payload.condition,
        input_data=input_dict,
        risk_score=prediction["risk_score"],
        risk_label=prediction["risk_label"],
        top_factors=top_factors,
        recommendations=recommendations,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return PredictionResult(
        assessment_id=record.id,
        condition=record.condition,
        risk_score=record.risk_score,
        risk_label=record.risk_label,
        top_factors=top_factors,
        recommendations=recommendations,
    )
