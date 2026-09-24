"""
API-level tests for POST /assessments -- the core "run a prediction" route,
end to end through the actual HTTP layer (unlike test_diabetes_model.py /
test_heart_disease_model.py, which call predict()/explain() directly).

Written for the same reason as test_history.py: this route had zero
automated coverage before this file, and /history turned out to have a
real bug hiding in exactly that gap.
"""
import uuid

from fastapi.testclient import TestClient

from app.api.deps import get_current_db_user
from app.db.database import get_db
from app.db.models import User
from app.main import app

client = TestClient(app)

DIABETES_PAYLOAD = {
    "condition": "diabetes",
    "age": 45, "sex": "female", "bmi": 27.5,
    "systolic_bp": 128, "diastolic_bp": 82,
    "glucose": 110, "cholesterol_total": 190,
    "smoker": False, "physically_active": True, "family_history": True,
}
HEART_DISEASE_PAYLOAD = {
    "condition": "heart_disease",
    "age": 61, "sex": "male", "bmi": 28.5,
    "systolic_bp": 152, "diastolic_bp": 88,
    "glucose": 130, "cholesterol_total": 260,
    "chest_pain_type": "asymptomatic", "exercise_angina": True,
    "smoker": True, "physically_active": False, "family_history": True,
}


def _make_user():
    """Fresh user, unique uid per test (see test_history.py for why this
    matters -- a shared dev sqlite file persists across runs)."""
    db = next(get_db())
    uid = f"test-assessments-{uuid.uuid4()}"
    user = User(firebase_uid=uid, email="assessments-test@example.com")
    db.add(user)
    db.commit()
    db.close()
    return uid


def _override_as(uid):
    """Re-queries fresh per request, matching how the real dependency
    works -- see test_history.py's _override_as for why a cached ORM
    object from a closed session breaks (DetachedInstanceError)."""

    def _get():
        db = next(get_db())
        return db.query(User).filter_by(firebase_uid=uid).first()

    return _get


def test_create_assessment_diabetes_happy_path():
    uid = _make_user()
    app.dependency_overrides[get_current_db_user] = _override_as(uid)
    try:
        resp = client.post("/api/v1/assessments", json=DIABETES_PAYLOAD)
        assert resp.status_code == 201
        body = resp.json()
        assert body["condition"] == "diabetes"
        assert 0.0 <= body["risk_score"] <= 1.0
        assert body["risk_label"] in {"low", "moderate", "high"}
        assert len(body["top_factors"]) > 0
        assert body["recommendations"]["specialist"]
        assert "assessment_id" in body
        assert "disclaimer" in body
    finally:
        app.dependency_overrides.pop(get_current_db_user, None)


def test_create_assessment_heart_disease_happy_path():
    uid = _make_user()
    app.dependency_overrides[get_current_db_user] = _override_as(uid)
    try:
        resp = client.post("/api/v1/assessments", json=HEART_DISEASE_PAYLOAD)
        assert resp.status_code == 201
        body = resp.json()
        assert body["condition"] == "heart_disease"
        assert 0.0 <= body["risk_score"] <= 1.0
        assert len(body["top_factors"]) > 0
    finally:
        app.dependency_overrides.pop(get_current_db_user, None)


def test_create_assessment_missing_chest_pain_type_returns_422():
    """Regression test: chest_pain_type is optional in the shared pydantic
    schema (it doesn't apply to diabetes requests) but required for
    heart_disease -- that check happens in predictor.py, surfaced by
    routes_assessment.py as a 422, not a 500. Manually verified once
    during the Firebase setup pass; locking it in here."""
    uid = _make_user()
    app.dependency_overrides[get_current_db_user] = _override_as(uid)
    try:
        payload = dict(HEART_DISEASE_PAYLOAD)
        payload.pop("chest_pain_type")
        resp = client.post("/api/v1/assessments", json=payload)
        assert resp.status_code == 422
        assert "chest_pain_type" in resp.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_current_db_user, None)


def test_create_assessment_rejects_out_of_range_input():
    """Pydantic-level validation (Field ge/le bounds), before the request
    ever reaches the model -- e.g. age=200 should never hit predict()."""
    uid = _make_user()
    app.dependency_overrides[get_current_db_user] = _override_as(uid)
    try:
        payload = dict(DIABETES_PAYLOAD, age=200)
        resp = client.post("/api/v1/assessments", json=payload)
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.pop(get_current_db_user, None)


def test_create_assessment_persists_and_appears_in_history():
    """Full integration: POST creates a row, GET /history finds it --
    exercises the same code path that Dashboard.jsx relies on."""
    uid = _make_user()
    app.dependency_overrides[get_current_db_user] = _override_as(uid)
    try:
        create_resp = client.post("/api/v1/assessments", json=DIABETES_PAYLOAD)
        assessment_id = create_resp.json()["assessment_id"]

        history_resp = client.get("/api/v1/history")
        returned_ids = {item["assessment_id"] for item in history_resp.json()}
        assert assessment_id in returned_ids
    finally:
        app.dependency_overrides.pop(get_current_db_user, None)


def test_create_assessment_requires_auth():
    """No override here on purpose -- exercises the REAL, un-mocked
    get_current_user dependency chain, not a stand-in. Sending literally
    no Authorization header short-circuits before Firebase Admin SDK is
    even touched (see firebase_auth.py's get_current_user), so this
    assertion holds regardless of whether this environment has real
    Firebase credentials configured -- unlike testing an actually-invalid
    token, which would need a real service account to reach that code
    path, and isn't practical to cover here. That slice was verified
    manually against a live Firebase project instead."""
    app.dependency_overrides.pop(get_current_db_user, None)  # ensure no leakage
    resp = client.post("/api/v1/assessments", json=DIABETES_PAYLOAD)
    assert resp.status_code == 401
