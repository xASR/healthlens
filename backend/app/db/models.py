"""
ORM models.

Note: we do NOT store passwords. `User.firebase_uid` is the link to the
identity Firebase already manages; this table just holds app-specific data
(display name, created_at) keyed to that uid.
"""
import datetime
import uuid

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    firebase_uid: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, index=True)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Assessment(Base):
    """One completed questionnaire + its prediction + its recommendations."""

    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)

    condition: Mapped[str] = mapped_column(String)  # "diabetes" | "heart_disease"

    # Raw questionnaire answers, stored as JSON so the schema can evolve
    # without a migration every time a field is added.
    input_data: Mapped[dict] = mapped_column(JSON)

    risk_score: Mapped[float] = mapped_column(Float)  # 0.0 - 1.0
    risk_label: Mapped[str] = mapped_column(String)  # "low" | "moderate" | "high"

    # Top SHAP factors, e.g. [{"feature": "glucose", "impact": 0.31}, ...]
    top_factors: Mapped[list] = mapped_column(JSON)

    # Generated diet/exercise/specialist suggestions
    recommendations: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, index=True
    )

    user: Mapped["User"] = relationship(back_populates="assessments")
