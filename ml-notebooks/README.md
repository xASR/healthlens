# ML Notebooks

This is where Week 3-4 work happens: dataset exploration, cleaning, model
training, and evaluation.

## Suggested notebook order

1. `01_data_exploration.ipynb` — load the Pima Indians Diabetes dataset
   into `data/raw/`, check class balance, missing/zero-as-missing values
   (this dataset famously has biologically-impossible zeros in glucose,
   blood pressure, BMI, etc. that need handling), correlations.
2. `02_preprocessing.ipynb` — clean, impute, and engineer features into
   `data/processed/`.
3. `03_model_training.ipynb` — train logistic regression as a baseline,
   then Random Forest / XGBoost; compare with train/test split + k-fold CV;
   pick the winner using ROC-AUC (not just accuracy, given class imbalance).
4. `04_export_model.ipynb` — wrap the winning model in a full sklearn
   `Pipeline` (preprocessing + estimator) and save it with:

   ```python
   import joblib
   joblib.dump(pipeline, "../backend/app/ml/artifacts/diabetes_model.joblib")
   ```

## Feature contract

The column order and names your pipeline is trained on **must** match
`FEATURE_ORDER["diabetes"]` in `backend/app/ml/predictor.py`:

```python
["age", "bmi", "glucose", "systolic_bp", "diastolic_bp",
 "cholesterol_total", "smoker", "physically_active", "family_history"]
```

If your dataset's columns don't line up 1:1 with this list (e.g. Pima
doesn't have blood pressure split into systolic/diastolic, or doesn't have
cholesterol at all), you have two options:
- Adjust `FEATURE_ORDER` and the questionnaire schema
  (`backend/app/schemas/questionnaire.py`) to match what you actually train on, or
- Engineer/impute the missing columns during preprocessing.

Either way, keep this file and `predictor.py` in sync — treat the feature
list as a contract between training and serving.

## Datasets (Section 16 of the proposal)

- Pima Indians Diabetes Dataset — Kaggle / UCI Machine Learning Repository
- UCI Heart Disease Dataset — UCI Machine Learning Repository

Download manually and place under `data/raw/` (gitignored — don't commit
raw data files).
