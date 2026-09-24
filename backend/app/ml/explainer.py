"""
Wraps a trained model with a SHAP explainer to produce the top contributing
factors behind a single prediction. Kept separate from predictor.py so the
API layer can request a prediction without explanation cheaply if it ever
needs to (e.g. bulk scoring), and request explanation only when showing
results to a user.
"""
import logging
from functools import lru_cache

import pandas as pd
import shap

from app.ml.predictor import load_model

logger = logging.getLogger(__name__)

TOP_N_FACTORS = 4


@lru_cache(maxsize=4)
def _get_explainer(condition: str):
    model = load_model(condition)
    # TreeExplainer works directly for RandomForest/XGBoost; if you end up
    # shipping a logistic regression as the final model, switch this to
    # shap.LinearExplainer or shap.Explainer(model, background_data).
    return shap.TreeExplainer(model)


def explain(condition: str, feature_frame: pd.DataFrame) -> list[dict]:
    """
    Returns the top contributing factors for this single prediction, sorted
    by absolute impact, e.g.:

        [
            {"feature": "glucose", "impact": 0.31, "value": 152},
            {"feature": "bmi", "impact": 0.18, "value": 29.4},
            ...
        ]

    Positive impact = pushed the prediction toward higher risk.
    """
    explainer = _get_explainer(condition)
    shap_values = explainer.shap_values(feature_frame)

    # For binary classifiers, shap_values may come back as a list
    # [class_0_values, class_1_values] -- we want the "at risk" class (1).
    values = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]

    contributions = [
        {
            "feature": feature,
            "impact": round(float(value), 4),
            "value": feature_frame.iloc[0][feature],
        }
        for feature, value in zip(feature_frame.columns, values)
    ]

    contributions.sort(key=lambda c: abs(c["impact"]), reverse=True)
    return contributions[:TOP_N_FACTORS]
