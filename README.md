# HealthLens

Explainable AI chronic disease risk screening — diabetes (primary) and
cardiovascular disease (secondary), built on the plan in
`Assessment_1_2023100000069.md`.

This repo is the **Week 2 deliverable**: full project scaffold, working
backend skeleton, working frontend skeleton, both verified to install and
run. No trained model yet — that's Week 3–4 (see Roadmap below).

## What's already working

- **Backend**: FastAPI app boots, all routes registered, SQLite DB
  auto-creates on startup, 5/5 tests passing (`pytest`).
- **Frontend**: React + Vite + Tailwind app builds clean (`npm run build`),
  full page flow wired: Landing → Register/Login → Questionnaire → Results
  (SHAP factors + recommendations + PDF) → Dashboard (risk trend chart).
- **Not working yet, on purpose**: predictions. `POST /api/v1/assessments`
  returns `503` until you train and drop in a real model — see Roadmap.

## Project layout

```
healthlens/
├── backend/                 FastAPI service
│   ├── app/
│   │   ├── main.py          App entrypoint, CORS, router registration
│   │   ├── core/             Settings (.env) + Firebase token verification
│   │   ├── db/                SQLAlchemy models (User, Assessment) + session
│   │   ├── schemas/          Pydantic request/response contracts
│   │   ├── ml/                predictor.py (inference) + explainer.py (SHAP)
│   │   │   └── artifacts/    <- trained .joblib models go here (Week 3-4)
│   │   ├── recommendations/  Rule-based diet/exercise/specialist engine
│   │   ├── api/               Route handlers (auth, assessments, history, reports)
│   │   └── utils/             PDF report generator (ReportLab)
│   └── tests/                pytest suite
├── frontend/                 React (Vite) SPA
│   └── src/
│       ├── firebase.js       Firebase client SDK init
│       ├── api/client.js     Axios client, auto-attaches Firebase ID token
│       ├── context/          Auth state (AuthContext)
│       ├── components/       Navbar, ProtectedRoute
│       └── pages/            Landing, Login, Register, Questionnaire, Results, Dashboard
├── ml-notebooks/              Where Week 3-4 dataset + training work happens
├── data/                       raw/ and processed/ dataset folders (gitignored)
└── docs/                        architecture.md
```

## Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # defaults work for local dev as-is
pytest                         # should show 5 passed
uvicorn app.main:app --reload  # http://localhost:8000/docs for interactive API docs
```

The server will start and log a warning that Firebase isn't configured yet
— that's expected until you complete the Firebase step below. `/health`
will work immediately.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env    # fill in Firebase values once you have them
npm run dev              # http://localhost:5173
```

### Firebase Authentication (needed before login/register actually work)

1. Create a project at https://console.firebase.google.com
2. Enable **Authentication → Sign-in method → Email/Password**
3. Project Settings → General → "Your apps" → add a Web app → copy the
   config values into `frontend/.env`
4. Project Settings → Service Accounts → **Generate new private key** →
   save the JSON as `backend/firebase-service-account.json` (already
   gitignored — never commit this file)

Once both are set, `frontend/.env` and `backend/firebase-service-account.json`
are all that connect the two halves to real auth.

## Roadmap (matches Section 13 of the proposal)

| Already done | Next up |
|---|---|
| Repo, env, both app skeletons (Week 2) | Collect + clean the Pima Diabetes dataset (Week 3) |
| Rule-based recommendation engine (unit tested) | Train + evaluate diabetes models in `ml-notebooks/`, save the winning pipeline to `backend/app/ml/artifacts/diabetes_model.joblib` (Week 4) |
| SHAP explainer module (code-complete, needs a real model to run against) | Once a model exists, `POST /api/v1/assessments` starts returning real predictions automatically — no other code changes needed |

### To unblock predictions specifically

`app/ml/predictor.py` expects a full sklearn **Pipeline** (preprocessing +
estimator) saved with `joblib.dump()`, with feature order matching
`FEATURE_ORDER["diabetes"]` in that same file. Train it in
`ml-notebooks/`, save it to `backend/app/ml/artifacts/diabetes_model.joblib`,
restart the API, and the whole assessment flow — prediction, SHAP
explanation, recommendations, history, PDF export — goes live with zero
other changes.

## Testing

```bash
cd backend && pytest -v          # unit tests: recommendation engine, health check
```

Add model evaluation tests (train/test split, k-fold CV, ROC-AUC, confusion
matrix) alongside the training notebook once the model exists, per Section 9
of the proposal.

## Disclaimer

HealthLens is a preliminary screening tool, not a diagnostic instrument.
This disclaimer is also shown in-app on every results page and PDF export.
