# HealthLens — AI Handoff Brief

**Purpose of this file:** paste/reference this at the start of a new AI chat (Claude,
Codex, or otherwise) so it can continue this project without you re-explaining
everything. It's also the fastest way to re-orient a teammate.

**How to use it:**
- New Claude chat → say: *"Clone https://github.com/YOUR_USERNAME/healthlens and
  read PROJECT_HANDOFF.md, then continue from the Roadmap section below."*
  (Claude's bash tool can reach github.com directly — no need to re-upload zips.)
- Codex → paste this file's contents as your first message/system context before
  assigning a task.

---

## 1. What this project is

**HealthLens** — a web app that screens for Type 2 diabetes and cardiovascular
risk from routine health indicators, using a trained ML model + SHAP
explainability (shows *why* a result came out the way it did, not just a score)
+ a rule-based recommendation engine (diet/exercise/specialist suggestions).

- **Course:** CSE474, Software Development and Project Management Lab, Section 5, Summer 2026
- **Team:** Four-Tier Tech — Alve Siddik (Team Lead, ML & Backend), Md Ataus Samad
  (Frontend), Md Aminul Islam Asif (QA & Testing), Md Kamrul Hasan (Docs & Deployment)
- **Weight:** 40% of course grade — also intended as a portfolio piece, so it
  needs to be genuinely rigorous, not just "working."
- **Deadline:** complete within this week.

## 2. Current status — what's actually done and verified (not aspirational)

- ✅ **Backend (FastAPI):** full app skeleton — auth token verification (Firebase),
  SQLAlchemy models, Pydantic schemas, ML prediction/explanation modules,
  rule-based recommendation engine, PDF export, all REST routes. Boots clean,
  16/16 pytest tests passing.
- ✅ **Diabetes model — trained, evaluated, and wired in for real:**
  - Dataset: Pima Indians Diabetes (768 records, NIDDK/UCI)
  - **Feature contract (must not drift):** `['pregnancies', 'glucose', 'diastolic_bp', 'bmi', 'age']`
  - Winner: **RandomForest**, test ROC-AUC **0.82**, 5-fold CV ROC-AUC **0.83**
  - Full executed notebook with real plots: `ml-notebooks/diabetes_model_training.ipynb`
  - Artifact saved at `backend/app/ml/artifacts/diabetes_model.joblib`
  - End-to-end verified: predict → SHAP explain → recommend, with a passing
    sanity check (low-risk scores below high-risk)
- ✅ **Heart disease model — trained, evaluated, and wired in for real:**
  - Dataset: UCI Heart Disease, Cleveland Clinic subset (303 records)
  - **Feature contract (must not drift):** `['age', 'sex', 'chest_pain_type', 'systolic_bp', 'cholesterol_total', 'fbs', 'exercise_angina']`
    — a deliberate 7-of-13 subset; see decision #6 below before changing it
  - Winner: **RandomForest**, test ROC-AUC **0.895**, 5-fold CV ROC-AUC **0.834**
  - Full executed notebook with real plots: `ml-notebooks/heart_disease_model_training.ipynb`
  - Artifact saved at `backend/app/ml/artifacts/heart_disease_model.joblib`
  - Required two new questionnaire fields (`chest_pain_type`, `exercise_angina`)
    — added to `schemas/questionnaire.py` and `Questionnaire.jsx`
  - End-to-end verified: predict → SHAP explain → recommend, incl. through
    the actual API route and a passing sanity check (low-risk < high-risk)
- ✅ **Frontend (React + Vite + Tailwind):** all pages built (Login, Register,
  Questionnaire, Results, Dashboard), builds clean with `npm run build`.
- ✅ **Real Firebase project connected and verified live, not just configured:**
  Email/Password auth enabled, `frontend/.env` and
  `backend/firebase-service-account.json` in place (both gitignored, per
  usual). Manually verified end-to-end on a real machine (not just this
  sandbox): register → login → submit assessment → view result → view
  dashboard history → download PDF report, all working through the actual
  UI, not just curl/pytest.
- ✅ **Two real bugs found and fixed during that manual verification pass**
  (both were latent since before this session — no API-level tests existed
  to catch them, see roadmap #2 below):
  - `GET /history` and `/history/{id}` 500'd on every call
    (`ResponseValidationError`) — `AssessmentHistoryItem.assessment_id` had
    no mapping to the DB model's actual `id` column. Fixed via
    `Field(validation_alias="id")`. Regression tests added:
    `backend/tests/test_history.py`.
  - The Results page's "Download PDF" button was a plain `<a href>` to an
    authenticated route — browser link navigation can't attach the bearer
    token, so it 401'd every time. Fixed by fetching the PDF as an
    authenticated blob (`downloadReport` in `frontend/src/api/client.js`)
    instead of linking directly.
- ⬜ **Not done yet:** live deployment, full E2E/UI test coverage (API-level
  coverage is partial now — `/history` has real tests, `/assessments` and
  `/auth/sync` still only have manual verification, not committed tests),
  technical report.

## 3. Key decisions already made — don't relitigate these without a reason

1. **Diabetes model excludes SkinThickness, Insulin, DiabetesPedigreeFunction**
   from the original 8 Pima columns. Why: they require lab measurements a
   self-screening user can't provide, and the first two are the dataset's
   least reliable columns anyway. Documented in `ml-notebooks/README.md`.
2. **Population bias is real and disclosed, not hidden:** Pima dataset =
   female patients only. `pregnancies` defaults to 0 for male users — a
   documented approximation, shown in the questionnaire UI itself. Same
   principle applied to heart disease (single-site, 68% male, ages 29-77) —
   see `ml-notebooks/README.md`'s heart disease limitations section.
3. **Model artifacts are saved as the RAW estimator, not a sklearn Pipeline.**
   Why: tree models need no scaling, and `shap.TreeExplainer` can't
   introspect through a `Pipeline` wrapper. If you ever swap in a non-tree
   model, this constraint changes. (LogisticRegression came close but lost
   to RandomForest on the heart disease comparison too — see
   `heart_disease_model_metrics.json` — so this hasn't been forced yet.)
4. **A real bug was found and fixed:** current `shap` versions return a 3D
   ndarray `(samples, features, classes)` from `TreeExplainer`, not the old
   list-of-arrays format. `backend/app/ml/explainer.py` handles both — don't
   revert this.
5. **Firebase Authentication is the one required external API** (per
   assignment rules) — verified genuinely free (no billing account, free to
   50k MAU). Google Places API was deliberately dropped — it requires
   enabling billing even to stay in its "free" tier.
6. **Heart disease model excludes restecg, thalach, oldpeak, slope, ca, thal**
   from the original 13 UCI columns — every one is the *output* of a cardiac
   workup (stress-test ECG, fluoroscopy, thallium scan), which a screening
   tool exists to tell someone whether they need. This is the dataset's
   strongest-predictor group, so it's a real, measured accuracy cost: our
   7-feature model gets 5-fold CV ROC-AUC 0.834 vs 0.891 for the same model
   given all 13 columns. `fbs` is trained on the dataset's real column but
   *derived* in the app from the `glucose` field already collected for
   diabetes (>120 mg/dL), rather than asked as a separate question. Full
   rationale and numbers in `ml-notebooks/README.md`.

## 4. Repo map

```
healthlens/
├── backend/app/          FastAPI app (see main.py for route registration)
│   ├── ml/                predictor.py (inference) + explainer.py (SHAP)
│   ├── ml/artifacts/       diabetes_model.joblib, heart_disease_model.joblib
│   ├── recommendations/  rule engine — keys off whatever features the model used
│   └── db/, schemas/, api/, core/
├── backend/tests/         19 tests, incl. 10 against the REAL trained models
│                          and 3 API-level tests against /history
├── ml-notebooks/          diabetes_model_training.ipynb, heart_disease_model_training.ipynb
│                          (both executed, real plots) + download_heart_data.py
├── frontend/src/pages/    Login, Register, Questionnaire, Results, Dashboard
└── docs/architecture.md
```

## 5. Roadmap — what's left, in priority order

1. **Full test coverage** — `/history` now has real API-level tests
   (`backend/tests/test_history.py`); `/assessments` and `/auth/sync` still
   only have manual verification, not committed tests. Given the bugs
   already found this way, prioritize this over polish elsewhere. Frontend
   E2E still not started.
2. **Deployment** — backend → Render, frontend → Vercel.
3. **Technical report** — should incorporate both notebooks' honest
   limitations sections (population bias, feature tradeoffs), not just
   describe features.

## 6. What "world-class" means for this project specifically

Not just "it works." The things that actually separate a top-tier submission:
- Every model claim is backed by a real evaluated number, not a guess
- Limitations are documented, not hidden (graders and portfolio readers both
  trust this more than a project that claims to be perfect)
- Tests actually run in CI, not just locally
- It's live at a real URL, not just localhost
- README is good enough that a stranger could run it in under 5 minutes
