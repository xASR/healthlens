"""
One-command download for the UCI Heart Disease (Cleveland) dataset.

data/README.md deliberately keeps this dataset out of git (unlike
pima_diabetes.csv) -- run this script once after cloning to fetch it
locally into data/raw/uci_heart_disease.csv.

Source: UCI Machine Learning Repository, "Heart Disease" dataset,
Cleveland Clinic Foundation subset (the only one of the 4 sites clean
enough for published ML work). 303 patients, 14 raw attributes.
https://archive.ics.uci.edu/dataset/45/heart+disease
"""
import sys
import urllib.request
from pathlib import Path

import pandas as pd

SOURCE_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "heart-disease/processed.cleveland.data"
)
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "uci_heart_disease.csv"

# Column order per the UCI documentation (heart-disease.names). The raw file
# has no header row.
COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
    "exang", "oldpeak", "slope", "ca", "thal", "num",
]


def main() -> None:
    print(f"Downloading {SOURCE_URL} ...")
    try:
        with urllib.request.urlopen(SOURCE_URL, timeout=30) as resp:
            raw_bytes = resp.read()
    except Exception as exc:  # network restrictions, UCI downtime, etc.
        print(f"ERROR: could not download dataset: {exc}", file=sys.stderr)
        print(
            "If your environment blocks archive.ics.uci.edu, download the "
            "file manually from the URL above and save it as "
            f"{OUT_PATH}, or fetch a mirror of 'processed.cleveland.data' "
            "and run this script's CSV conversion on it directly.",
            file=sys.stderr,
        )
        sys.exit(1)

    from io import StringIO

    df = pd.read_csv(StringIO(raw_bytes.decode("utf-8")), header=None, names=COLUMNS, na_values="?")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Saved {len(df)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
