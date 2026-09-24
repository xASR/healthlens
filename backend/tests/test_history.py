"""
API-level tests for GET /history and GET /history/{id}.

Written as a direct regression test for a real bug: AssessmentHistoryItem
declared `assessment_id` but the Assessment DB model's primary key column
is `id`, with no alias between them. FastAPI's response_model validation
raised a 500 ResponseValidationError on every call -- this went uncaught
by the existing unit tests (which call predict()/explain() directly, not
through HTTP) since there was no API-level test for this route. Fixed via
`Field(validation_alias="id")` in schemas/prediction.py.
"""
import uuid

from fastapi.testclient import TestClient

from app.api.deps import get_current_db_user
from app.db.database import get_db
from app.db.models import Assessment, User
from app.main import app

client = TestClient(app)


def _make_user_with_assessments(n=2):
    """Creates a fresh user (unique uid, so repeated test runs against a
    shared dev sqlite file don't collide) with n assessments. Returns the
    uid (not the ORM object -- see _override_as, which re-queries fresh
    per request instead of reusing a session that's since been closed)."""
    db = next(get_db())
    uid = f"test-history-{uuid.uuid4()}"
    user = User(firebase_uid=uid, email="history-test@example.com")
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id

    ids = []
    for i in range(n):
        a = Assessment(
            id=str(uuid.uuid4()),
            user_id=user_id,
            condition="diabetes" if i % 2 == 0 else "heart_disease",
            input_data={},
            risk_score=0.5,
            risk_label="moderate",
            top_factors=[{"feature": "glucose", "value": 130, "impact": 0.2}],
            recommendations={"diet": [], "exercise": [], "specialist": "GP"},
        )
        db.add(a)
        ids.append(a.id)
    db.commit()
    db.close()
    return uid, ids


def _override_as(uid):
    """Real get_current_db_user re-queries fresh every request via its own
    request-scoped session (see deps.py) -- this override mirrors that,
    rather than handing back one cached ORM object whose original session
    may already be closed by the time the route touches its attributes."""

    def _get():
        db = next(get_db())
        return db.query(User).filter_by(firebase_uid=uid).first()

    return _get


def test_history_list_returns_200_with_assessment_id_field():
    uid, ids = _make_user_with_assessments(2)
    app.dependency_overrides[get_current_db_user] = _override_as(uid)
    try:
        resp = client.get("/api/v1/history")
        assert resp.status_code == 200
        body = resp.json()
        returned_ids = {item["assessment_id"] for item in body}
        assert set(ids).issubset(returned_ids)
        assert all("condition" in item and "risk_score" in item for item in body)
    finally:
        app.dependency_overrides.pop(get_current_db_user, None)


def test_history_single_item_still_works():
    uid, ids = _make_user_with_assessments(1)
    app.dependency_overrides[get_current_db_user] = _override_as(uid)
    try:
        resp = client.get(f"/api/v1/history/{ids[0]}")
        assert resp.status_code == 200
        assert resp.json()["assessment_id"] == ids[0]
    finally:
        app.dependency_overrides.pop(get_current_db_user, None)


def test_history_is_scoped_to_the_requesting_user():
    """One user must never see another user's assessments."""
    uid_a, ids_a = _make_user_with_assessments(1)
    uid_b, _ = _make_user_with_assessments(1)
    app.dependency_overrides[get_current_db_user] = _override_as(uid_b)
    try:
        resp = client.get("/api/v1/history")
        returned_ids = {item["assessment_id"] for item in resp.json()}
        assert not returned_ids.intersection(ids_a)
    finally:
        app.dependency_overrides.pop(get_current_db_user, None)
