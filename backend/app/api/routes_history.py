from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_db_user
from app.db.database import get_db
from app.db.models import Assessment, User
from app.schemas.prediction import AssessmentHistoryItem

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[AssessmentHistoryItem])
def list_history(
    current_user: User = Depends(get_current_db_user),
    db: Session = Depends(get_db),
):
    """Powers the risk-trend dashboard chart -- one point per past assessment."""
    return (
        db.query(Assessment)
        .filter_by(user_id=current_user.id)
        .order_by(Assessment.created_at.asc())
        .all()
    )


@router.get("/{assessment_id}")
def get_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_db_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(Assessment)
        .filter_by(id=assessment_id, user_id=current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    return {
        "assessment_id": record.id,
        "condition": record.condition,
        "input_data": record.input_data,
        "risk_score": record.risk_score,
        "risk_label": record.risk_label,
        "top_factors": record.top_factors,
        "recommendations": record.recommendations,
        "created_at": record.created_at,
    }
