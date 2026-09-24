# ML Notebooks

## Status: diabetes model trained, evaluated, and live in the backend

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

## Feature decision (read this before retraining or extending)

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

## Known limitation: population bias

This dataset covers **female Pima Indian patients, age 21+, only**. Any
model trained on it inherits that population bias. `pregnancies` defaults to
`0` for male users in the app (see `_to_feature_frame` in `predictor.py`) —
a documented approximation, not a validated clinical assumption. This is
disclosed in the questionnaire UI itself and belongs in the technical
report's limitations section, not glossed over.

## Feature contract

Column order in `backend/app/ml/predictor.py`'s `FEATURE_ORDER["diabetes"]`
**must** match training exactly:

```python
["pregnancies", "glucose", "diastolic_bp", "bmi", "age"]
```

## Artifact format: raw estimator, not a Pipeline

We save the raw `RandomForestClassifier`, not wrapped in a sklearn
`Pipeline`. Tree models need no feature scaling, and `shap.TreeExplainer`
requires the raw estimator directly — it can't introspect through a
`Pipeline` wrapper. If a future model swap picks a non-tree model, this
constraint (and the SHAP explainer type in `explainer.py`) needs revisiting.

## Next: heart disease model (same pattern)

Not started yet. Same pipeline shape applies:
1. Source the UCI Heart Disease dataset (Cleveland subset is the common
   clean starting point)
2. Repeat the same EDA → feature-selection-with-rationale → compare →
   export pattern as this notebook
3. Update `FEATURE_ORDER["heart_disease"]` in `predictor.py` to match
   whatever feature set you actually train on (it currently holds a
   placeholder guess, not a verified contract)
4. Export to `backend/app/ml/artifacts/heart_disease_model.joblib` — the
   API picks it up automatically, no other code changes needed
