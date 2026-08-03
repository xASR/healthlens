"""
Firebase Authentication integration.

The frontend signs the user in with the Firebase JS SDK and attaches the
resulting ID token to every API request as:

    Authorization: Bearer <firebase_id_token>

This module verifies that token server-side. We never see or store passwords
-- Firebase owns identity, we only trust its verified tokens.
"""
import logging
import os

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

from app.core.config import settings

logger = logging.getLogger(__name__)
_bearer_scheme = HTTPBearer(auto_error=False)

_firebase_app = None


def init_firebase() -> None:
    """Initialize the Firebase Admin SDK once, at API startup."""
    global _firebase_app
    if _firebase_app is not None:
        return

    if not os.path.exists(settings.firebase_credentials_path):
        logger.warning(
            "Firebase credentials not found at %s. Auth-protected routes will "
            "reject all requests until you add a real service account file. "
            "See .env.example.",
            settings.firebase_credentials_path,
        )
        return

    cred = credentials.Certificate(settings.firebase_credentials_path)
    _firebase_app = firebase_admin.initialize_app(cred)
    logger.info("Firebase Admin SDK initialized.")


async def get_current_user(
    credentials_header: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    """
    FastAPI dependency: verifies the bearer token and returns the decoded
    Firebase user claims (uid, email, etc). Use as:

        @router.get("/me")
        def me(user: dict = Depends(get_current_user)):
            return {"uid": user["uid"]}
    """
    if credentials_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    if _firebase_app is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service not configured. Add a Firebase service account "
            "file and set FIREBASE_CREDENTIALS_PATH.",
        )

    try:
        decoded_token = firebase_auth.verify_id_token(credentials_header.credentials)
        return decoded_token
    except Exception as exc:  # firebase_admin raises several distinct exception types
        logger.info("Token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        ) from exc
