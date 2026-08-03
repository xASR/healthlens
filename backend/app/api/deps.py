from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.firebase_auth import get_current_user
from app.db.database import get_db
from app.db.models import User


def get_current_db_user(
    user_claims: dict = Depends(get_current_user), db: Session = Depends(get_db)
) -> User:
    """
    Resolves the verified Firebase token into our local User row.
    Raises 404 if the frontend hasn't called POST /auth/sync yet.
    """
    user = db.query(User).filter_by(firebase_uid=user_claims["uid"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found locally. Call POST /auth/sync first.",
        )
    return user
