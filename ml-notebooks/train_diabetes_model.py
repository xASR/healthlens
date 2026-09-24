"""
Diabetes model training pipeline.

Dataset: Pima Indians Diabetes Database (NIDDK / UCI), 768 records, all
female patients of Pima Indian heritage, age 21+. This is a real and
important limitation -- documented explicitly below, not hidden.

Feature decision: the raw dataset has 8 columns. We deliberately train on
only 5 of them: Pregnancies, Glucose, BloodPressure, BMI, Age.

We EXCLUDE:
  - SkinThickness, Insulin: not usable in a self-report questionnaire (they
    require a caliper measurement / lab test most people never have done),
    AND they carry the dataset's worst missingness (~30-48% zero-as-missing
    for these two columns specifically, per known analyses of this dataset)
  - DiabetesPedigreeFunction: a composite genetic-risk score a layperson
    cannot self-report. We already collect a simple boolean
    "family_history" in the questionnaire for the recommendation layer;
    we do not force a proxy value into the trained model for it.

This keeps the model's inputs limited to what a real self-screening user
can plausibly answer, at some cost to raw predictive power versus using
all 8 original columns -- a deliberate, documented UX-vs-accuracy tradeoff.
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

RAW_PATH = "data/raw/pima_diabetes.csv"
ARTIFACT_PATH = "backend/app/ml/artifacts/diabetes_model.joblib"
METRICS_PATH = "ml-notebooks/diabetes_model_metrics.json"

FEATURES = ["Pregnancies", "Glucose", "BloodPressure", "BMI", "Age"]
FEATURE_RENAME = {
    "Pregnancies": "pregnancies",
    "Glucose": "glucose",
    "BloodPressure": "diastolic_bp",
    "BMI": "bmi",
    "Age": "age",
}
TARGET = "Outcome"

print("=" * 70)
print("STEP 1: Load + inspect")
print("=" * 70)
df = pd.read_csv(RAW_PATH)
print(f"Shape: {df.shape}")
print(f"Class balance:\n{df[TARGET].value_counts(normalize=True).round(3)}")

print("\n" + "=" * 70)
print("STEP 2: Clean -- zero-as-missing handling for the columns we keep")
print("=" * 70)
# Glucose and BMI can never legitimately be 0 in a living person; those
# zeros are missing-value placeholders in this dataset. BloodPressure=0 is
# also implausible. Pregnancies=0 and Age are legitimate as-is.
zero_as_missing_cols = ["Glucose", "BloodPressure", "BMI"]
for col in zero_as_missing_cols:
    n_zero = (df[col] == 0).sum()
    print(f"{col}: {n_zero} zero-values ({n_zero/len(df):.1%}) treated as missing")
    median_val = df.loc[df[col] != 0, col].median()
    df[col] = df[col].replace(0, np.nan).fillna(median_val)

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

# Baseline -- logistic regression needs scaling; tree models don't.
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
    print(classification_report(y_test, pred, target_names=["No Diabetes", "Diabetes"]))

print("\n" + "=" * 70)
print("STEP 5: Select winner (by test ROC-AUC -- robust to class imbalance)")
print("=" * 70)
winner_name = max(results, key=lambda k: results[k]["test_roc_auc"])
winner_model = candidates[winner_name]
print(f"Winner: {winner_name} (ROC-AUC = {results[winner_name]['test_roc_auc']})")

print("\n" + "=" * 70)
print("STEP 6: Export")
print("=" * 70)
# IMPORTANT: for tree models we save the raw estimator, NOT wrapped in a
# Pipeline. Two reasons: (1) tree models need no feature scaling, and
# (2) shap.TreeExplainer requires the raw tree estimator directly -- it
# cannot introspect through a Pipeline wrapper.
joblib.dump(winner_model, ARTIFACT_PATH)
print(f"Saved winning model ({winner_name}) to {ARTIFACT_PATH}")

with open(METRICS_PATH, "w") as f:
    json.dump({"winner": winner_name, "features": list(FEATURE_RENAME.values()), "results": results}, f, indent=2)
print(f"Saved metrics to {METRICS_PATH}")

print("\nFeature order contract for predictor.py:")
print(list(FEATURE_RENAME.values()))
