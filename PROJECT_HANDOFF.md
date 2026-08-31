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
  10/10 pytest tests passing.
- ✅ **Diabetes model — trained, evaluated, and wired in for real:**
  - Dataset: Pima Indians Diabetes (768 records, NIDDK/UCI)
  - **Feature contract (must not drift):** `['pregnancies', 'glucose', 'diastolic_bp', 'bmi', 'age']`
  - Winner: **RandomForest**, test ROC-AUC **0.82**, 5-fold CV ROC-AUC **0.83**
  - Full executed notebook with real plots: `ml-notebooks/diabetes_model_training.ipynb`
  - Artifact saved at `backend/app/ml/artifacts/diabetes_model.joblib`
  - End-to-end verified: predict → SHAP explain → recommend, with a passing
    sanity check (low-risk scores below high-risk)
- ✅ **Frontend (React + Vite + Tailwind):** all pages built (Login, Register,
  Questionnaire, Results, Dashboard), builds clean with `npm run build`.
- ⬜ **Not done yet:** heart disease model, real Firebase project connected,
  live deployment, full E2E/UI test coverage, technical report.

## 3. Key decisions already made — don't relitigate these without a reason

1. **Diabetes model excludes SkinThickness, Insulin, DiabetesPedigreeFunction**
   from the original 8 Pima columns. Why: they require lab measurements a
   self-screening user can't provide, and the first two are the dataset's
   least reliable columns anyway. Documented in `ml-notebooks/README.md`.
2. **Population bias is real and disclosed, not hidden:** Pima dataset =
   female patients only. `pregnancies` defaults to 0 for male users — a
   documented approximation, shown in the questionnaire UI itself.
3. **Model artifacts are saved as the RAW estimator, not a sklearn Pipeline.**
   Why: tree models need no scaling, and `shap.TreeExplainer` can't
   introspect through a `Pipeline` wrapper. If you ever swap in a non-tree
   model, this constraint changes.
4. **A real bug was found and fixed:** current `shap` versions return a 3D
   ndarray `(samples, features, classes)` from `TreeExplainer`, not the old
   list-of-arrays format. `backend/app/ml/explainer.py` handles both — don't
   revert this.
5. **Firebase Authentication is the one required external API** (per
   assignment rules) — verified genuinely free (no billing account, free to
   50k MAU). Google Places API was deliberately dropped — it requires
   enabling billing even to stay in its "free" tier.

## 4. Repo map

```
healthlens/
├── backend/app/          FastAPI app (see main.py for route registration)
│   ├── ml/                predictor.py (inference) + explainer.py (SHAP)
│   ├── ml/artifacts/       diabetes_model.joblib lives here
│   ├── recommendations/  rule engine — keys off whatever features the model used
│   └── db/, schemas/, api/, core/
├── backend/tests/         10 tests, incl. 5 against the REAL trained model
├── ml-notebooks/          diabetes_model_training.ipynb (executed, real plots)
├── frontend/src/pages/    Login, Register, Questionnaire, Results, Dashboard
└── docs/architecture.md
```

## 5. Roadmap — what's left, in priority order

1. **Heart disease model** — same pattern as diabetes: source UCI Heart
   Disease dataset, EDA → feature-selection-with-rationale → compare 3
   models → export. Update `FEATURE_ORDER["heart_disease"]` in
   `predictor.py` (currently a placeholder, not a verified contract).
2. **Real Firebase project** — create at console.firebase.google.com, enable
   Email/Password auth, drop config into `frontend/.env` and
   `backend/firebase-service-account.json`.
3. **Full test coverage** — unit tests exist; still need API-level tests
   (Postman/pytest+httpx against live routes) and basic frontend E2E.
4. **Deployment** — backend → Render, frontend → Vercel.
5. **Technical report** — should incorporate the notebook's honest
   limitations section (population bias, feature tradeoffs), not just
   describe features.

## 6. What "world-class" means for this project specifically

Not just "it works." The things that actually separate a top-tier submission:
- Every model claim is backed by a real evaluated number, not a guess
- Limitations are documented, not hidden (graders and portfolio readers both
  trust this more than a project that claims to be perfect)
- Tests actually run in CI, not just locally
- It's live at a real URL, not just localhost
- README is good enough that a stranger could run it in under 5 minutes
