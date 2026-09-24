# HealthLens

Explainable AI chronic disease risk screening — diabetes (primary, **trained
and live**) and cardiovascular disease (secondary, not started yet).

## What's already working

- **Backend**: FastAPI app boots, all routes registered, SQLite DB
  auto-creates on startup, **10/10 tests passing** (`pytest`), 5 of those
  against the actual trained model.
- **Diabetes predictions are live and real.** `POST /api/v1/assessments`
  returns a genuine risk score (RandomForest, test ROC-AUC 0.82), a SHAP
  explanation of the top contributing factors, and rule-based
  recommendations — verified end-to-end from a clean clone, not just
  locally.
- **Frontend**: React + Vite + Tailwind app builds clean (`npm run build`),
  full page flow wired: Landing → Register/Login → Questionnaire → Results
  (SHAP factors + recommendations + PDF) → Dashboard (risk trend chart).
- **Not working yet, on purpose**: heart disease predictions (no model
  trained for that condition yet — see Roadmap), and real Firebase
  auth isn't connected (needs your own Firebase project — see below).

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
│   │   │   └── artifacts/    diabetes_model.joblib lives here (committed, ~1.1MB)
│   │   ├── recommendations/  Rule-based diet/exercise/specialist engine
│   │   ├── api/               Route handlers (auth, assessments, history, reports)
│   │   └── utils/             PDF report generator (ReportLab)
│   └── tests/                pytest suite (10 tests)
├── frontend/                 React (Vite) SPA
│   └── src/
│       ├── firebase.js       Firebase client SDK init
│       ├── api/client.js     Axios client, auto-attaches Firebase ID token
│       ├── context/          Auth state (AuthContext)
│       ├── components/       Navbar, ProtectedRoute
│       └── pages/            Landing, Login, Register, Questionnaire, Results, Dashboard
├── ml-notebooks/              diabetes_model_training.ipynb (executed, real plots)
├── data/                       raw/ and processed/ dataset folders
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
pytest                         # should show 10 passed
uvicorn app.main:app --reload  # http://localhost:8000/docs for interactive API docs
```

The server will start and log a warning that Firebase isn't configured yet
— that's expected until you complete the Firebase step below. `/health`
will work immediately, and so will diabetes predictions via `/docs`.

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

## Roadmap

| Done | Next up |
|---|---|
| Full backend + frontend scaffold | Heart disease model (same pattern as diabetes — see `ml-notebooks/README.md`) |
| Diabetes model trained, evaluated, and live (RandomForest, test ROC-AUC 0.82) | Real Firebase project connected |
| SHAP explainability verified against the real model | Deployment (backend → Render, frontend → Vercel) |
| Rule-based recommendation engine (unit tested) | Full API/E2E test coverage, not just unit tests |
| 10/10 backend tests passing, incl. 5 against the real model | Technical report |

### Adding the heart disease model

`app/ml/predictor.py` loads whatever's saved at
`app/ml/artifacts/heart_disease_model.joblib` — a **raw tree estimator**
(e.g. `RandomForestClassifier`), **not** wrapped in a sklearn `Pipeline`.
This matters: tree models need no feature scaling, and `shap.TreeExplainer`
(used in `explainer.py`) can't introspect through a `Pipeline` wrapper —
saving one there will silently break explanations. Update
`FEATURE_ORDER["heart_disease"]` in `predictor.py` to match whatever
features you actually train on (it currently holds a placeholder guess,
not a verified contract), following the same pattern as the diabetes model.

## Testing

```bash
cd backend && pytest -v
```

10 tests: health check, recommendation engine (rule logic, no model
needed), and 5 tests against the actual trained diabetes model
(`test_diabetes_model.py`) — prediction validity, model direction sanity,
SHAP ranking, and the full predict→explain→recommend pipeline end to end.

## Disclaimer

HealthLens is a preliminary screening tool, not a diagnostic instrument.
This disclaimer is also shown in-app on every results page and PDF export.
