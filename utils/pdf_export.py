"""
utils/pdf_export.py
-------------------
Export a study plan to a well-formatted PDF using ReportLab.
Returns raw bytes so Streamlit can offer a download button.
"""

from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ---------------------------------------------------------------------------
# Brand colours
# ---------------------------------------------------------------------------
PRIMARY   = colors.HexColor("#4F46E5")   # indigo
SECONDARY = colors.HexColor("#7C3AED")   # violet
ACCENT    = colors.HexColor("#06B6D4")   # cyan
BG_LIGHT  = colors.HexColor("#F8F7FF")
TEXT_DARK = colors.HexColor("#1E1B4B")


def _build_styles():
    base = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "EduTitle",
        parent=base["Title"],
        fontSize=24,
        textColor=PRIMARY,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "EduSubtitle",
        parent=base["Normal"],
        fontSize=11,
        textColor=SECONDARY,
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    h2_style = ParagraphStyle(
        "EduH2",
        parent=base["Heading2"],
        fontSize=14,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    h3_style = ParagraphStyle(
        "EduH3",
        parent=base["Heading3"],
        fontSize=11,
        textColor=SECONDARY,
        spaceBefore=8,
        spaceAfter=3,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "EduBody",
        parent=base["Normal"],
        fontSize=9,
        leading=14,
        textColor=TEXT_DARK,
        spaceAfter=3,
    )
    bullet_style = ParagraphStyle(
        "EduBullet",
        parent=body_style,
        leftIndent=14,
        bulletIndent=4,
    )

    return {
        "title":    title_style,
        "subtitle": subtitle_style,
        "h2":       h2_style,
        "h3":       h3_style,
        "body":     body_style,
        "bullet":   bullet_style,
    }


def _md_to_flowables(text: str, styles: dict) -> list:
    """
    Very lightweight markdown → ReportLab flowables converter.
    Handles: ## headings, ### headings, - bullets, ** bold **, plain text.
    """
    flowables = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            flowables.append(Spacer(1, 4))
            continue

        if stripped.startswith("## "):
            flowables.append(Paragraph(stripped[3:], styles["h2"]))
        elif stripped.startswith("### "):
            flowables.append(Paragraph(stripped[4:], styles["h3"]))
        elif stripped.startswith("#### "):
            flowables.append(Paragraph(f"<b>{stripped[5:]}</b>", styles["body"]))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            content = stripped[2:]
            content = _bold_md(content)
            flowables.append(Paragraph(f"• {content}", styles["bullet"]))
        elif stripped.startswith("| "):
            # Skip markdown table lines in the PDF (they look bad in plain text)
            flowables.append(Paragraph(stripped.replace("|", " ").strip(), styles["body"]))
        else:
            flowables.append(Paragraph(_bold_md(stripped), styles["body"]))

    return flowables


def _bold_md(text: str) -> str:
    """Convert **bold** to <b>bold</b> for ReportLab."""
    import re
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def export_plan_to_pdf(
    goal: str,
    level: str,
    hours: float,
    seven_day: str,
    thirty_day: str,
    daily_goals: str,
) -> bytes:
    """
    Build and return a PDF as bytes.

    Parameters match the keys returned by agents.planner.generate_study_plan().
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = _build_styles()
    story  = []

    # ---- Cover block -------------------------------------------------------
    story.append(Paragraph("EduMentor AI", styles["title"]))
    story.append(Paragraph("Personalised Learning Plan", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=10))

    # Meta table
    meta_data = [
        ["Learning Goal", goal],
        ["Skill Level",   level],
        ["Daily Hours",   f"{hours} hours/day"],
        ["Generated",     datetime.utcnow().strftime("%d %b %Y %H:%M UTC")],
    ]
    meta_table = Table(meta_data, colWidths=[4 * cm, 13 * cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BG_LIGHT),
        ("TEXTCOLOR",  (0, 0), (0, -1), PRIMARY),
        ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, BG_LIGHT]),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E7FF")),
        ("PADDING",    (0, 0), (-1, -1), 6),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 16))

    # ---- Daily Goals (quick reference) ------------------------------------
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))
    story.append(Paragraph("⚡ Week 1 — Daily Goals at a Glance", styles["h2"]))
    story.extend(_md_to_flowables(daily_goals, styles))

    # ---- 7-Day Plan -------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))
    story.extend(_md_to_flowables(seven_day, styles))

    # ---- 30-Day Roadmap ---------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))
    story.extend(_md_to_flowables(thirty_day, styles))

    # ---- Footer note ------------------------------------------------------
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY))
    story.append(Paragraph(
        "Generated by EduMentor AI · Powered by Google Gemini · "
        "Kaggle 5-Day AI Agents Intensive Capstone",
        ParagraphStyle("footer", parent=styles["body"],
                       fontSize=7, textColor=colors.grey, alignment=TA_CENTER),
    ))

    doc.build(story)
    return buffer.getvalue()
