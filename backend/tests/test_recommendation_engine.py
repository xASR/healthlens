from app.recommendations.engine import build_recommendations


def test_high_glucose_triggers_diet_advice():
    top_factors = [{"feature": "glucose", "impact": 0.4, "value": 160}]
    rec = build_recommendations("diabetes", "high", top_factors)

    assert any("carbohydrate" in tip.lower() for tip in rec["diet"])
    assert rec["specialist"] == "Endocrinologist -- consult promptly"


def test_negative_impact_factor_is_not_actioned():
    # A factor that's LOWERING risk shouldn't generate a "fix this" tip.
    top_factors = [{"feature": "glucose", "impact": -0.2, "value": 85}]
    rec = build_recommendations("diabetes", "low", top_factors)

    assert rec["diet"] == [
        "Maintain a balanced, whole-food diet as a general preventive measure."
    ]


def test_low_risk_specialist_is_general_physician():
    rec = build_recommendations("heart_disease", "low", [])
    assert rec["specialist"] == "General physician (routine annual screening)"


def test_dedupe_keeps_unique_tips_in_order():
    top_factors = [
        {"feature": "glucose", "impact": 0.5, "value": 160},
        {"feature": "bmi", "impact": 0.3, "value": 31},
    ]
    rec = build_recommendations("diabetes", "high", top_factors)
    assert len(rec["diet"]) == len(set(rec["diet"]))
