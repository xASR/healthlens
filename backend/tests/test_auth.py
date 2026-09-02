"""
API-level tests for POST /auth/sync and GET /auth/me.

Unlike test_assessments.py and test_history.py, these two routes depend
directly on get_current_user (raw Firebase claims dict), not
get_current_db_user (a resolved local User row) -- so the override here
is a plain claims dict, not a re-query function.
"""
import uuid

from fastapi.testclient import TestClient

from app.core.firebase_auth import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.main import app

client = TestClient(app)


def _claims(uid=None, email=None):
    return {
        "uid": uid or f"test-auth-{uuid.uuid4()}",
        "email": email or "auth-test@example.com",
        "name": "Test User",
    }


def test_sync_creates_new_user():
    claims = _claims()
    app.dependency_overrides[get_current_user] = lambda: claims
    try:
        resp = client.post("/api/v1/auth/sync")
        assert resp.status_code == 200
        body = resp.json()
        assert body["created"] is True
        assert body["email"] == claims["email"]
        assert body["id"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_sync_is_idempotent():
    """Calling sync twice for the same Firebase user must not create a
    second local row -- User.firebase_uid is a unique column, so a bug
    here would surface as an IntegrityError on the second call."""
    claims = _claims()
    app.dependency_overrides[get_current_user] = lambda: claims
    try:
        first = client.post("/api/v1/auth/sync").json()
        second = client.post("/api/v1/auth/sync").json()
        assert first["id"] == second["id"]
        assert second["created"] is False

        db = next(get_db())
        matching = db.query(User).filter_by(firebase_uid=claims["uid"]).all()
        assert len(matching) == 1
        db.close()
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_me_before_sync_does_not_error():
    """Documents existing behavior: /auth/me for an unsynced uid returns
    200 with a detail message, not a 404 -- unlike get_current_db_user
    (used by /assessments, /history), which does raise 404 in the
    equivalent case. Inconsistent between the two, but this test locks in
    what /auth/me actually does today rather than assuming either way."""
    claims = _claims()
    app.dependency_overrides[get_current_user] = lambda: claims
    try:
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 200
        assert "not synced" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_me_after_sync_returns_user():
    claims = _claims()
    app.dependency_overrides[get_current_user] = lambda: claims
    try:
        client.post("/api/v1/auth/sync")
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == claims["email"]
        assert "detail" not in body
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_sync_requires_auth():
    """No override -- exercises the real dependency chain, same caveat as
    test_assessments.py's equivalent test (see that file for why only the
    no-token case, not an invalid-token case, is practical to test here)."""
    app.dependency_overrides.pop(get_current_user, None)
    resp = client.post("/api/v1/auth/sync")
    assert resp.status_code == 401
