# HealthLens Architecture

Three-tier design, matching Section 10 of the project proposal.

```
┌─────────────────────┐
│   React SPA (Vite)  │  Auth screens, questionnaire, results, dashboard
└──────────┬───────────┘
           │ HTTPS + Firebase ID token (Authorization: Bearer <token>)
           ▼
┌──────────────────────┐
│   Firebase Auth       │  Owns identity. Issues/verifies tokens.
└──────────┬───────────┘
           │ verified uid + claims
           ▼
┌──────────────────────┐
│  FastAPI (app/)        │  Validates requests, orchestrates the pipeline
│  ├─ api/                Route handlers
│  ├─ core/                 Settings + Firebase token verification
│  ├─ ml/                    predictor.py -> explainer.py (SHAP)
│  ├─ recommendations/  Rule engine (SHAP factors -> diet/exercise/specialist)
│  └─ db/                     SQLAlchemy models + session
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  SQLite / PostgreSQL   │  users, assessments (history)
└──────────────────────┘
```

## Request flow: submitting an assessment

1. Frontend collects the questionnaire, calls `POST /api/v1/assessments`
   with the Firebase ID token attached.
2. `core/firebase_auth.py` verifies the token; `api/deps.py` resolves it to
   a local `User` row.
3. `ml/predictor.py` loads the trained sklearn pipeline for the requested
   condition and returns a risk score + the feature row used.
4. `ml/explainer.py` runs a SHAP `TreeExplainer` over that same row to
   rank the top contributing factors.
5. `recommendations/engine.py` maps positive-impact factors above their
   trigger thresholds to diet/exercise tips and a specialist suggestion.
6. The full result is persisted as an `Assessment` row and returned to the
   frontend, which renders it and offers a PDF export
   (`utils/pdf_generator.py`, via `GET /api/v1/reports/{id}/pdf`).

## Why these choices

- **Firebase Auth instead of custom auth**: removes password hashing,
  session/token management, and reset-flow security surface from a
  solo-developer timeline.
- **SHAP `TreeExplainer`**: exact and fast for tree-based models
  (RandomForest/XGBoost), which is what Section 13's Week 4 plan trains
  and compares. If the winning model ends up being logistic regression
  instead, swap in `shap.LinearExplainer` in `ml/explainer.py` — nothing
  else in the pipeline needs to change.
- **Rule-based recommendations, not a second model**: the mapping from "a
  factor is elevated" to "here's the guideline-based advice" is a citeable,
  auditable rule, not a prediction — keeping it rule-based makes it easy to
  reference sources for the technical report.
- **JSON columns for `input_data` / `top_factors` / `recommendations`**:
  the questionnaire and explanation shape will evolve as features are
  added (e.g. heart disease has a different feature set); JSON columns
  avoid a migration every time that happens.
