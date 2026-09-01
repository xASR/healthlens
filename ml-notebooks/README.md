# ML Notebooks

## Status: both models trained, evaluated, and live in the backend

`diabetes_model_training.ipynb` is executed end-to-end (not just written —
run it yourself and diff the outputs) and covers:

1. Load + class balance check (768 records, ~65/35 split)
2. Zero-as-missing imputation for Glucose/BloodPressure/BMI
3. Feature selection rationale (see below)
4. Correlation analysis
5. Three-way model comparison: Logistic Regression, Random Forest, XGBoost
   — compared on 5-fold CV **and** held-out test ROC-AUC, not just accuracy
6. Confusion matrix + ROC curve for the winner
7. SHAP summary plot verifying explainability works on the actual model
8. Export to `backend/app/ml/artifacts/diabetes_model.joblib`

**Result:** RandomForest won (test ROC-AUC 0.82, 5-fold CV 0.83 — consistent
with each other, so not overfit to one split). Full metrics in
`diabetes_model_metrics.json`.

`train_diabetes_model.py` is the same pipeline as a plain script, useful for
quick retraining without opening Jupyter.

`heart_disease_model_training.ipynb` follows the identical shape (see its
own section below) and is likewise executed end-to-end, with
`train_heart_disease_model.py` as the script equivalent.

## Diabetes: feature decision (read this before retraining or extending)

The raw dataset has 8 predictor columns. We train on only **5**:
`Pregnancies`, `Glucose`, `BloodPressure`, `BMI`, `Age`.

Excluded on purpose:
- **SkinThickness, Insulin** — require a caliper measurement / lab test most
  users have never had. Also the dataset's least reliable columns.
- **DiabetesPedigreeFunction** — a composite genetic score a layperson can't
  self-report. We collect a simple `family_history` boolean instead, used by
  the recommendation layer, not forced into the model as a fake proxy.

This is a deliberate UX-vs-accuracy tradeoff, not an oversight — documented
in the notebook's conclusion section too.

## Diabetes: known limitation — population bias

This dataset covers **female Pima Indian patients, age 21+, only**. Any
model trained on it inherits that population bias. `pregnancies` defaults to
`0` for male users in the app (see `_to_feature_frame` in `predictor.py`) —
a documented approximation, not a validated clinical assumption. This is
disclosed in the questionnaire UI itself and belongs in the technical
report's limitations section, not glossed over.

## Diabetes: feature contract

Column order in `backend/app/ml/predictor.py`'s `FEATURE_ORDER["diabetes"]`
**must** match training exactly:

```python
["pregnancies", "glucose", "diastolic_bp", "bmi", "age"]
```

## Artifact format: raw estimator, not a Pipeline

We save the raw estimator (`RandomForestClassifier` for both models
currently), not wrapped in a sklearn `Pipeline`. Tree models need no feature
scaling, and `shap.TreeExplainer` requires the raw estimator directly — it
can't introspect through a `Pipeline` wrapper. If a future model swap picks
a non-tree model (LogisticRegression came close on the heart disease
comparison — see below), this constraint, and the SHAP explainer type in
`explainer.py`, need revisiting: switch to `shap.LinearExplainer` or
`shap.Explainer(model, background_data)`.

---

## Heart disease: source data

`data/raw/uci_heart_disease.csv` is **not committed** (see `data/README.md`)
— run `python ml-notebooks/download_heart_data.py` from the repo root once
to fetch it. UCI Heart Disease dataset, Cleveland Clinic Foundation subset
(the only one of the dataset's 4 collection sites clean enough for
published ML work), 303 patients, 14 raw columns.

## Heart disease: feature decision (read this before retraining or extending)

The raw file has 13 predictor columns. We train on only **7**: `age`,
`sex`, `cp` (chest pain type), `trestbps` (resting BP), `chol`
(cholesterol), `fbs` (fasting blood sugar), `exang` (exercise-induced
angina).

Excluded on purpose — **restecg, thalach, oldpeak, slope, ca, thal**: every
one of these is the *output of a cardiac workup* (resting/exercise ECG, a
supervised treadmill stress test, cardiac fluoroscopy, or a thallium
stress test). A self-screening tool exists to tell someone whether they
should go get that workup in the first place — requiring its results as
input would be circular. Also worth being honest: these are the dataset's
*strongest* predictors (`thal` r=0.53, `ca` r=0.46 vs target) and the two
columns with actual missing data (`ca`: 4 rows, `thal`: 2 rows), so this is
a real, measured accuracy tradeoff:

| | 5-fold CV ROC-AUC |
|---|---|
| Our 7-feature (self-reportable only) RandomForest | **0.834** |
| Same model, all 13 raw columns (incl. workup outputs, `ca`/`thal` median-imputed) | 0.891 |

`fbs` is a genuine training column here (the dataset's own boolean), but in
the app it's **not asked as a separate question** — it's derived from the
same fasting-glucose value already collected for the diabetes model
(`glucose > 120` → `fbs = 1`). See `_to_feature_frame` in `predictor.py`.

`chest_pain_type` and `exercise_angina` are new questionnaire fields
(schemas/questionnaire.py, Questionnaire.jsx) that didn't exist before this
model — everything else reuses fields already collected for diabetes.

Same treatment as the diabetes model: `bmi`, `diastolic_bp`, `smoker`,
`physically_active`, `family_history` stay in the questionnaire for the
recommendation engine but aren't trained-model inputs — no equivalent
column exists in this dataset (the raw 76-attribute UCI files do have
`smoke`/`famhist` fields, but they're missing across most patients and no
published research uses them — same rationale as excluding
SkinThickness/Insulin above).

## Heart disease: known limitations

- **Single site, 1980s cohort:** Cleveland Clinic only.
- **Sex skew:** 68% male / 32% female.
- **Age range:** 29–77, mean 54 — an older, already-symptomatic outpatient
  population, not a general screening population.
- **Self-report reliability:** `cp` and `exang` were clinician-recorded in
  this dataset, not patient-self-reported. A layperson's own categorization
  of their chest pain may be noisier than what training reflects — a real,
  if unmeasured, source of potential real-world performance drop-off.
- **Small dataset:** 303 records vs 768 for diabetes.

**Result:** RandomForest won (test ROC-AUC 0.895, 5-fold CV 0.834 —
reasonably consistent). Full metrics in `heart_disease_model_metrics.json`.

## Heart disease: feature contract

Column order in `backend/app/ml/predictor.py`'s
`FEATURE_ORDER["heart_disease"]` **must** match training exactly:

```python
["age", "sex", "chest_pain_type", "systolic_bp", "cholesterol_total", "fbs", "exercise_angina"]
```

`chest_pain_type` encoding (`CHEST_PAIN_TYPE_MAP` in `predictor.py`, must
match the UCI `cp` column):

```python
{"typical_angina": 1, "atypical_angina": 2, "non_anginal_pain": 3, "asymptomatic": 4}
```
