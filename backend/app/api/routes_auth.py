"""
Auth-adjacent routes. Firebase handles the actual login/register UI and
issues the token; this router just keeps a local `users` row in sync so we
have a stable user_id to attach assessments to.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.firebase_auth import get_current_user
from app.db.database import get_db
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sync")
def sync_user(
    user_claims: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Call this once right after the frontend signs a user in with Firebase.
    Creates the local user record on first login, otherwise no-ops.
    """
    existing = db.query(User).filter_by(firebase_uid=user_claims["uid"]).first()
    if existing:
        return {"id": existing.id, "email": existing.email, "created": False}

    new_user = User(
        firebase_uid=user_claims["uid"],
        email=user_claims.get("email", ""),
        display_name=user_claims.get("name"),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email, "created": True}


@router.get("/me")
def read_current_user(
    user_claims: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(firebase_uid=user_claims["uid"]).first()
    if not user:
        return {"detail": "User not synced yet. Call POST /auth/sync first."}
    return {"id": user.id, "email": user.email, "display_name": user.display_name}
