"""
Heart disease model training pipeline.

Dataset: UCI Heart Disease dataset, Cleveland Clinic Foundation subset
(the only one of the dataset's 4 sites clean enough for published ML
work), 303 patients. Run download_heart_data.py first to fetch it.

Feature decision: the raw processed Cleveland file has 13 predictor
columns. We deliberately train on only 7: age, sex, cp, trestbps, chol,
fbs, exang.

We EXCLUDE: restecg, thalach, oldpeak, slope, ca, thal -- every one of
these is the *output of a cardiac workup* (resting/exercise ECG, a
supervised treadmill stress test, cardiac fluoroscopy, a thallium
stress test). A self-screening tool exists to tell someone whether they
should go get that workup in the first place; requiring its results as
input would be circular. These are also the dataset's strongest
predictors (|r| up to 0.53 vs target) and the two with actual missing
values (ca: 4, thal: 2) -- so this is a real accuracy tradeoff, not a
free lunch, same as excluding SkinThickness/Insulin from the diabetes
model.

We KEEP fbs (fasting blood sugar > 120 mg/dl) as a real training column
here, using the dataset's own boolean. In the app, this is DERIVED from
the same fasting-glucose value already collected for the diabetes model
(glucose > 120 -> fbs=1) rather than asked as a separate question --
see _to_feature_frame in predictor.py. Training on the dataset's actual
fbs values (not a proxy) keeps the model itself honest; only the app's
input-collection step reuses an existing field for UX convenience.

This keeps the model's inputs limited to what a real self-screening
user can plausibly report from routine vitals / recent bloodwork or
answer directly (chest pain type, exercise-induced chest pain) -- at
some cost to raw predictive power versus using all 13 original columns,
a deliberate, documented UX-vs-accuracy tradeoff (see
ml-notebooks/README.md for the full rationale and correlation numbers).
"""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

RAW_PATH = "data/raw/uci_heart_disease.csv"
ARTIFACT_PATH = "backend/app/ml/artifacts/heart_disease_model.joblib"
METRICS_PATH = "ml-notebooks/heart_disease_model_metrics.json"

FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "exang"]
FEATURE_RENAME = {
    "age": "age",
    "sex": "sex",
    "cp": "chest_pain_type",
    "trestbps": "systolic_bp",
    "chol": "cholesterol_total",
    "fbs": "fbs",
    "exang": "exercise_angina",
}
RAW_TARGET = "num"  # 0 = no disease, 1-4 = increasing severity of presence
TARGET = "target"

print("=" * 70)
print("STEP 1: Load + inspect")
print("=" * 70)
df = pd.read_csv(RAW_PATH)
print(f"Shape: {df.shape}")
df[TARGET] = (df[RAW_TARGET] > 0).astype(int)
print(f"Class balance (binarized presence/absence):\n{df[TARGET].value_counts(normalize=True).round(3)}")

print("\n" + "=" * 70)
print("STEP 2: Missingness check on the columns we actually use")
print("=" * 70)
# ca and thal carry this dataset's only missing values (4 and 2 rows) --
# both are excluded columns, so this pipeline needs no imputation at all.
for col in FEATURES:
    n_missing = df[col].isna().sum()
    print(f"{col}: {n_missing} missing")
assert df[FEATURES].isna().sum().sum() == 0, "Unexpected missingness in selected features"

print("\n" + "=" * 70)
print("STEP 3: Train/test split (stratified, 80/20)")
print("=" * 70)
X = df[FEATURES].rename(columns=FEATURE_RENAME)
y = df[TARGET]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")

print("\n" + "=" * 70)
print("STEP 4: Train + compare models")
print("=" * 70)

results = {}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

log_reg = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))])
rf = RandomForestClassifier(n_estimators=300, max_depth=5, min_samples_leaf=5, random_state=42)
xgb = XGBClassifier(
    n_estimators=200, max_depth=3, learning_rate=0.05, eval_metric="logloss", random_state=42
)

candidates = {"LogisticRegression": log_reg, "RandomForest": rf, "XGBoost": xgb}

for name, model in candidates.items():
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="roc_auc")
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    pred = model.predict(X_test)

    results[name] = {
        "cv_roc_auc_mean": round(cv_scores.mean(), 4),
        "cv_roc_auc_std": round(cv_scores.std(), 4),
        "test_roc_auc": round(roc_auc_score(y_test, proba), 4),
        "test_accuracy": round(accuracy_score(y_test, pred), 4),
        "test_precision": round(precision_score(y_test, pred), 4),
        "test_recall": round(recall_score(y_test, pred), 4),
        "test_f1": round(f1_score(y_test, pred), 4),
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
    }
    print(f"\n--- {name} ---")
    print(f"5-fold CV ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    print(f"Test ROC-AUC:      {results[name]['test_roc_auc']:.4f}")
    print(f"Test Accuracy:     {results[name]['test_accuracy']:.4f}")
    print(classification_report(y_test, pred, target_names=["No Disease", "Disease"]))

print("\n" + "=" * 70)
print("STEP 5: Select winner (by test ROC-AUC -- robust to class imbalance)")
print("=" * 70)
winner_name = max(results, key=lambda k: results[k]["test_roc_auc"])
winner_model = candidates[winner_name]
print(f"Winner: {winner_name} (ROC-AUC = {results[winner_name]['test_roc_auc']})")

print("\n" + "=" * 70)
print("STEP 6: Export")
print("=" * 70)
# Same artifact-format rule as the diabetes model: tree models are saved
# as the raw estimator (no Pipeline) so shap.TreeExplainer can introspect
# them directly. If LogisticRegression wins, we keep it wrapped in its
# Pipeline (it needs the scaler) -- explainer.py detects the model type
# at explain-time and picks TreeExplainer vs a model-agnostic Explainer
# accordingly. See explainer.py's _get_explainer.
joblib.dump(winner_model, ARTIFACT_PATH)
print(f"Saved winning model ({winner_name}) to {ARTIFACT_PATH}")

with open(METRICS_PATH, "w") as f:
    json.dump(
        {"winner": winner_name, "features": list(FEATURE_RENAME.values()), "results": results},
        f,
        indent=2,
    )
print(f"Saved metrics to {METRICS_PATH}")

print("\nFeature order contract for predictor.py:")
print(list(FEATURE_RENAME.values()))
