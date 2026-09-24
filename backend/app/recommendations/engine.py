"""
Rule-based recommendation engine.

Deliberately NOT ML-based: the mapping from "which factor is driving risk"
to "what should the user do about it" is a set of well-established,
explainable health guidelines. Keeping it rule-based also means it's easy
to review, cite sources for, and adjust without retraining anything.

Extend RULES to cover more features as your model's feature set grows.
"""
from typing import Literal

Condition = Literal["diabetes", "heart_disease"]

# Each rule fires when `feature` appears among the top contributing factors
# with a positive impact (i.e. it's pushing risk UP), and the user's raw
# value crosses `trigger_if`. Add citations in comments as you finalize
# these for the technical report.
RULES: dict[str, list[dict]] = {
    "glucose": [
        {
            "trigger_if": lambda v: v >= 100,
            "diet": [
                "Reduce refined carbohydrates and added sugars (white bread, "
                "sugary drinks, pastries).",
                "Favor high-fiber foods -- vegetables, legumes, whole grains "
                "-- which slow glucose absorption.",
            ],
            "exercise": [
                "Aim for at least 150 minutes/week of moderate activity "
                "(brisk walking, cycling); it improves insulin sensitivity.",
            ],
        }
    ],
    "bmi": [
        {
            "trigger_if": lambda v: v >= 25,
            "diet": [
                "Target a modest calorie deficit (~500 kcal/day) for gradual, "
                "sustainable weight loss rather than crash dieting.",
            ],
            "exercise": [
                "Combine cardio with 2x/week resistance training to preserve "
                "muscle mass while losing weight.",
            ],
        }
    ],
    "systolic_bp": [
        {
            "trigger_if": lambda v: v >= 130,
            "diet": [
                "Reduce sodium intake; consider a DASH-style eating pattern "
                "(fruits, vegetables, low-fat dairy).",
            ],
            "exercise": [
                "Regular aerobic exercise can meaningfully lower blood "
                "pressure over 4-8 weeks of consistency.",
            ],
        }
    ],
    "cholesterol_total": [
        {
            "trigger_if": lambda v: v >= 200,
            "diet": [
                "Limit saturated/trans fats; increase soluble fiber (oats, "
                "beans) and omega-3 sources (fatty fish, flaxseed).",
            ],
            "exercise": [
                "Regular moderate exercise helps raise HDL ('good') "
                "cholesterol.",
            ],
        }
    ],
}

SPECIALISTS: dict[Condition, dict[str, str]] = {
    "diabetes": {
        "low": "General physician (routine annual screening)",
        "moderate": "Endocrinologist or diabetes educator",
        "high": "Endocrinologist -- consult promptly",
    },
    "heart_disease": {
        "low": "General physician (routine annual screening)",
        "moderate": "Cardiologist",
        "high": "Cardiologist -- consult promptly",
    },
}

URGENCY_NOTES = {
    "low": "Your indicators are currently in a lower-risk range. Keep up "
    "regular checkups.",
    "moderate": "Some indicators suggest elevated risk. Consider scheduling "
    "a checkup in the coming weeks.",
    "high": "Multiple indicators suggest meaningfully elevated risk. We "
    "recommend consulting a healthcare professional soon.",
}


def build_recommendations(
    condition: Condition, risk_label: str, top_factors: list[dict]
) -> dict:
    diet: list[str] = []
    exercise: list[str] = []

    for factor in top_factors:
        if factor["impact"] <= 0:
            continue  # only act on factors pushing risk UP
        rules = RULES.get(factor["feature"], [])
        for rule in rules:
            try:
                if rule["trigger_if"](float(factor["value"])):
                    diet.extend(rule["diet"])
                    exercise.extend(rule["exercise"])
            except (TypeError, ValueError):
                continue  # non-numeric value (e.g. boolean factor) -- skip

    if not diet:
        diet = ["Maintain a balanced, whole-food diet as a general preventive measure."]
    if not exercise:
        exercise = ["Maintain at least 150 minutes/week of moderate physical activity."]

    return {
        "diet": _dedupe(diet),
        "exercise": _dedupe(exercise),
        "specialist": SPECIALISTS[condition][risk_label],
        "urgency_note": URGENCY_NOTES[risk_label],
    }


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
