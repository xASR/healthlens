from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_db_user
from app.db.database import get_db
from app.db.models import Assessment, User
from app.utils.pdf_generator import generate_assessment_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{assessment_id}/pdf")
def download_report(
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

    pdf_bytes = generate_assessment_pdf(
        {
            "condition": record.condition,
            "created_at": record.created_at.strftime("%Y-%m-%d %H:%M"),
            "risk_score": record.risk_score,
            "risk_label": record.risk_label,
            "top_factors": record.top_factors,
            "recommendations": record.recommendations,
        },
        user_email=current_user.email,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="healthlens_{assessment_id[:8]}.pdf"'},
    )
