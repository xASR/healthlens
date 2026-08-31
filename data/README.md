# Data

`raw/pima_diabetes.csv` (23KB, public research dataset) is **committed** —
small enough that anyone cloning this repo can re-run
`ml-notebooks/diabetes_model_training.ipynb` immediately with zero manual
download steps.

Larger or less clearly-licensed datasets (e.g. the UCI Heart Disease
dataset, once that work starts) should stay out of git and follow a
download-it-yourself pattern instead — `raw/` and `processed/` remain
gitignored by default for anything you don't explicitly force-add.

- `raw/pima_diabetes.csv` — Pima Indians Diabetes Dataset (committed)
- `raw/uci_heart_disease.csv` — UCI Heart Disease Dataset (not yet added — download when starting that model)

`processed/` is where cleaned/feature-engineered versions go, produced by
the notebooks in `ml-notebooks/`.
