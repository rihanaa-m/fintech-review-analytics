"""Generate Week 2 final submission report PDF."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Week_2_Final_Report.pdf"
PLOTS = ROOT / "analysis_outputs" / "task4"
RECOMMENDATIONS = PLOTS / "recommendations.json"


def _load_stats():
    stats = {"banks": {}, "total": 0}
    analyzed = ROOT / "data" / "processed" / "reviews_analyzed.csv"
    if analyzed.is_file():
        import pandas as pd

        df = pd.read_csv(analyzed)
        stats["total"] = len(df)
        for bank, g in df.groupby("bank"):
            stats["banks"][bank] = {
                "count": len(g),
                "avg_rating": round(g["rating"].mean(), 2),
                "pct_pos": round(100 * (g["sentiment_label"] == "positive").mean(), 1),
                "pct_neg": round(100 * (g["sentiment_label"] == "negative").mean(), 1),
            }
    if RECOMMENDATIONS.is_file():
        stats["recommendations"] = json.loads(RECOMMENDATIONS.read_text(encoding="utf-8"))
    return stats


def build_story():
    styles = getSampleStyleSheet()
    title = ParagraphStyle("T", parent=styles["Title"], fontSize=18, alignment=TA_CENTER,
                           textColor=colors.HexColor("#1a365d"))
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=12, spaceBefore=10, spaceAfter=5,
                        textColor=colors.HexColor("#2c5282"))
    body = ParagraphStyle("B", parent=styles["BodyText"], fontSize=9.5, leading=13, alignment=TA_JUSTIFY)
    stats = _load_stats()

    s = []
    s.append(Paragraph("Week 2 Final Report", title))
    s.append(Paragraph("Fintech Review Analytics — Google Play Store Analysis", title))
    s.append(Paragraph("[Your Name] | Omega Consultancy | May 2026",
                      ParagraphStyle("m", parent=body, alignment=TA_CENTER, fontSize=9)))
    s.append(Spacer(1, 0.3 * cm))

    s.append(Paragraph("Executive Summary", h1))
    s.append(Paragraph(
        f"We analyzed <b>{stats.get('total', 1200)}</b> Google Play reviews across CBE, BOA, and Dashen "
        "mobile banking apps using a reproducible pipeline: scraping, preprocessing, DistilBERT sentiment "
        "classification, TF-IDF thematic analysis, PostgreSQL storage, and stakeholder visualizations. "
        "Findings highlight BOA as the weakest experience profile and CBE as the strongest average rating, "
        "with transaction performance and account access as dominant negative themes.",
        body,
    ))

    s.append(Paragraph("1. Methodology", h1))
    s.append(Paragraph(
        "<b>Data:</b> google-play-scraper (country et, English), ≥400 reviews/bank. "
        "<b>Sentiment:</b> distilbert-base-uncased-finetuned-sst-2-english; confidence &lt;0.55 → neutral. "
        "<b>Themes:</b> keyword rules aligned to five business categories, validated with TF-IDF terms per bank. "
        "<b>Database:</b> PostgreSQL bank_reviews schema (banks, reviews).",
        body,
    ))

    s.append(Paragraph("2. Data Quality", h1))
    if stats["banks"]:
        rows = [["Bank", "Reviews", "Avg rating", "% Positive", "% Negative"]]
        for bank, v in stats["banks"].items():
            rows.append([bank, str(v["count"]), str(v["avg_rating"]),
                         f"{v['pct_pos']}%", f"{v['pct_neg']}%"])
        t = Table(rows, colWidths=[2.5 * cm, 2 * cm, 2.5 * cm, 3 * cm, 3 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ]))
        s.append(t)
    else:
        s.append(Paragraph("Run full pipeline to populate statistics.", body))

    s.append(PageBreak())
    s.append(Paragraph("3. Sentiment & Thematic Findings", h1))
    for plot_name, caption in [
        ("01_sentiment_by_bank.png", "Figure 1. Sentiment distribution by bank"),
        ("02_rating_by_bank.png", "Figure 2. Star rating distribution"),
        ("03_theme_frequency.png", "Figure 3. Theme frequency by bank"),
    ]:
        path = PLOTS / plot_name
        s.append(Paragraph(f"<b>{caption}</b>", body))
        if path.is_file():
            s.append(Image(str(path), width=14 * cm, height=8 * cm))
        s.append(Spacer(1, 0.2 * cm))

    s.append(Paragraph("4. Bank-Specific Recommendations", h1))
    recs = stats.get("recommendations", {})
    for bank in ["CBE", "BOA", "Dashen"]:
        if bank not in recs:
            continue
        r = recs[bank]
        s.append(Paragraph(f"<b>{bank}</b> (avg rating {r.get('avg_rating', 'N/A')})", body))
        s.append(Paragraph("<b>Drivers:</b> " + "; ".join(r.get("satisfaction_drivers", [])), body))
        s.append(Paragraph("<b>Pain points:</b> " + "; ".join(r.get("pain_points", [])), body))
        s.append(Paragraph("<b>Actions:</b> " + "; ".join(r.get("recommendations", [])), body))
        s.append(Spacer(1, 0.15 * cm))

    s.append(Paragraph("5. Limitations & Ethics", h1))
    s.append(Paragraph(
        "Reviews reflect voluntary, polarized feedback; English-only preprocessing may miss Amharic comments. "
        "Play Store sampling is not a random survey. Sentiment model is binary SST-2 extended with a neutral band. "
        "Recommendations should be validated with in-app analytics and support ticket data.",
        body,
    ))

    s.append(Paragraph("6. Next Steps", h1))
    s.append(Paragraph(
        "Integrate in-app telemetry, A/B test transfer flow improvements, deploy support chatbot intents "
        "from top complaint themes, and refresh quarterly scraping for trend monitoring.",
        body,
    ))
    return s


def main():
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=1.8 * cm, leftMargin=1.8 * cm,
                            topMargin=1.6 * cm, bottomMargin=1.6 * cm)
    doc.build(build_story())
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()
