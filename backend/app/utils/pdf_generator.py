"""
Generates a shareable one-page PDF summary of a single assessment.
"""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_assessment_pdf(assessment: dict, user_email: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("HealthLens Risk Assessment Summary", styles["Title"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"Prepared for: {user_email}", styles["Normal"]))
    story.append(Paragraph(f"Date: {assessment['created_at']}", styles["Normal"]))
    story.append(Spacer(1, 0.6 * cm))

    story.append(
        Paragraph(
            f"Condition screened: {assessment['condition'].replace('_', ' ').title()}",
            styles["Heading2"],
        )
    )
    story.append(
        Paragraph(
            f"Risk score: {assessment['risk_score']:.0%} "
            f"({assessment['risk_label'].title()} risk)",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Top Contributing Factors", styles["Heading2"]))
    factor_rows = [["Factor", "Your Value", "Relative Impact"]]
    for f in assessment["top_factors"]:
        factor_rows.append([f["feature"].replace("_", " ").title(), str(f["value"]), f"{f['impact']:+.3f}"])
    table = Table(factor_rows, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Recommendations", styles["Heading2"]))
    rec = assessment["recommendations"]
    story.append(Paragraph("<b>Diet:</b> " + " ".join(rec["diet"]), styles["Normal"]))
    story.append(Paragraph("<b>Exercise:</b> " + " ".join(rec["exercise"]), styles["Normal"]))
    story.append(
        Paragraph(f"<b>Suggested specialist:</b> {rec['specialist']}", styles["Normal"])
    )
    story.append(Spacer(1, 0.6 * cm))

    story.append(
        Paragraph(
            "<i>HealthLens is a preliminary screening tool, not a medical "
            "diagnosis. Please consult a qualified healthcare professional "
            "for evaluation.</i>",
            styles["Normal"],
        )
    )

    doc.build(story)
    return buffer.getvalue()
