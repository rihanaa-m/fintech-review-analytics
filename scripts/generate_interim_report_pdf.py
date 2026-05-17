"""Generate Week 2 interim submission report PDF (max 5 pages)."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Week_2_Interim_Report.pdf"
CHART = ROOT / "analysis_outputs" / "task2" / "sentiment_by_bank_interim.png"


def bullets(items, style):
    return ListFlowable(
        [ListItem(Paragraph(i, style), leftIndent=10) for i in items],
        bulletType="bullet",
        leftIndent=16,
    )


def build_story():
    styles = getSampleStyleSheet()
    title = ParagraphStyle("T", parent=styles["Title"], fontSize=18, alignment=TA_CENTER, spaceAfter=10,
                           textColor=colors.HexColor("#1a365d"))
    subtitle = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=11, alignment=TA_CENTER, spaceAfter=16)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=13, spaceBefore=12, spaceAfter=6,
                        textColor=colors.HexColor("#2c5282"))
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=11, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("B", parent=styles["BodyText"], fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)
    small = ParagraphStyle("S", parent=body, fontSize=9, textColor=colors.grey)

    s = []

    s.append(Paragraph("Week 2 Interim Report", title))
    s.append(Paragraph("Customer Experience Analytics for Fintech Apps", subtitle))
    s.append(Paragraph(
        "<b>Omega Consultancy</b> — Google Play Store review analysis for "
        "CBE, Bank of Abyssinia (BOA), and Dashen Bank<br/>"
        "<b>Author:</b> [Your Name] &nbsp;|&nbsp; <b>Date:</b> 17 May 2026",
        ParagraphStyle("meta", parent=small, alignment=TA_CENTER),
    ))
    s.append(Spacer(1, 0.4 * cm))

    # Executive summary
    s.append(Paragraph("Executive Summary", h1))
    s.append(Paragraph(
        "This interim submission documents completion of <b>Task 1</b> (data collection and preprocessing) "
        "and early progress on <b>Task 2</b> (sentiment analysis) for the Week 2 fintech challenge. "
        "We scraped <b>1,200 Google Play reviews</b> (400 per bank), produced a clean analysis-ready dataset "
        "with zero missing required fields, and ran an initial <b>VADER</b> sentiment pass to surface early "
        "patterns ahead of full <b>DistilBERT</b> classification planned for the final submission.",
        body,
    ))

    # 1. Business context
    s.append(Paragraph("1. Business Context", h1))
    s.append(Paragraph(
        "Ethiopian banks compete on mobile experience. Play Store reviews provide unfiltered signals on "
        "transfers, login reliability, UI quality, and feature requests. Omega Consultancy needs evidence-backed "
        "insights for three clients: Commercial Bank of Ethiopia (CBE), Bank of Abyssinia (BOA), and Dashen Bank.",
        body,
    ))

    # 2. Scraping methodology
    s.append(Paragraph("2. Scraping Methodology (Task 1)", h1))
    s.append(Paragraph("<b>Tools and targets</b>", h2))
    s.append(bullets([
        "<b>Library:</b> google-play-scraper (Python)",
        "<b>Storefront:</b> country <font face='Courier'>et</font>, language <font face='Courier'>en</font>",
        "<b>Sort:</b> newest first; 200 reviews per API batch with continuation tokens",
        "<b>Target:</b> ≥400 reviews per bank (minimum 1,200 total)",
    ], body))

    apps = [
        ["Bank", "App ID", "Play Store name"],
        ["CBE", "com.combanketh.mobilebanking", "Commercial Bank of Ethiopia"],
        ["BOA", "com.boa.boaMobileBanking", "BoA Mobile"],
        ["Dashen", "com.dashen.dashensuperapp", "Dashen Bank"],
    ]
    t = Table(apps, colWidths=[2.2 * cm, 6.5 * cm, 6.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
    ]))
    s.append(t)
    s.append(Spacer(1, 0.2 * cm))
    s.append(Paragraph(
        "<b>Preprocessing pipeline:</b> deduplicate by <font face='Courier'>review_id</font>; drop rows missing "
        "text or rating; normalize dates to YYYY-MM-DD; export columns "
        "<font face='Courier'>review, rating, date, bank, source</font>. "
        "Raw JSON and CSV files are gitignored and stored locally under <font face='Courier'>data/raw/</font>.",
        body,
    ))

    # 3. Data quality
    s.append(Paragraph("3. Data Quality Summary", h1))
    quality = [
        ["Metric", "Value"],
        ["Total reviews", "1,200"],
        ["Reviews per bank", "400 each (CBE, BOA, Dashen)"],
        ["Date range", "2025-06-21 to 2026-05-16"],
        ["Missing review / rating / date", "0%"],
        ["Duplicate review_id removed", "0 (clean scrape)"],
        ["Mean star rating (all banks)", "3.93 / 5"],
        ["Mean review length", "~44 characters"],
    ]
    t2 = Table(quality, colWidths=[7 * cm, 8 * cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ]))
    s.append(t2)
    s.append(Spacer(1, 0.15 * cm))

    rating_bank = [
        ["Bank", "Mean rating", "Interpretation"],
        ["CBE", "4.16", "Highest average rating among the three"],
        ["Dashen", "3.98", "Mid-range; strong positive review share in early NLP"],
        ["BOA", "3.66", "Lowest average; higher negative share in early NLP"],
    ]
    t3 = Table(rating_bank, colWidths=[2.5 * cm, 3 * cm, 9.5 * cm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a5568")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ]))
    s.append(Paragraph("<b>Star rating by bank</b>", h2))
    s.append(t3)

    s.append(PageBreak())

    # 4. Early sentiment
    s.append(Paragraph("4. Early Sentiment Findings (Task 2 — Interim)", h1))
    s.append(Paragraph(
        "<b>Interim method:</b> VADER (lexicon-based) applied to all 1,200 cleaned reviews. "
        "Labels: positive (compound ≥ 0.05), negative (≤ −0.05), neutral otherwise. "
        "<b>Final submission plan:</b> DistilBERT SST-2 (<font face='Courier'>distilbert-base-uncased-finetuned-sst-2-english</font>) "
        "with low-confidence predictions mapped to neutral, per the challenge brief.",
        body,
    ))

    sent = [
        ["Bank", "Avg compound", "% Positive", "% Negative", "Early read"],
        ["CBE", "+0.29", "69.3%", "10.3%", "Strongest positive tone; aligns with highest stars"],
        ["Dashen", "+0.30", "66.8%", "13.5%", "Generally favorable; watch OTP/login themes in text"],
        ["BOA", "+0.19", "52.8%", "17.3%", "Weakest sentiment profile; more negative language"],
    ]
    t4 = Table(sent, colWidths=[2 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 5.5 * cm])
    t4.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    s.append(t4)
    s.append(Spacer(1, 0.25 * cm))
    s.append(Paragraph("<b>Figure 1.</b> Sentiment distribution by bank (VADER, interim)", h2))
    if CHART.is_file():
        s.append(Image(str(CHART), width=15 * cm, height=8.5 * cm))
    else:
        s.append(Paragraph("<i>Chart not found — run scripts/generate_interim_report_pdf.py after sentiment chart is built.</i>", small))
    s.append(Paragraph(
        "<b>Key interim insight:</b> CBE and Dashen show a clear majority of positive language, while BOA "
        "has the largest negative share (~17%) and lowest mean star rating (3.66), suggesting priority areas "
        "for product and support teams (e.g. transfer speed, login/OTP reliability) in the final thematic analysis.",
        body,
    ))

    # 5. Repository status
    s.append(Paragraph("5. Repository and Git Status", h1))
    s.append(bullets([
        "<b>Repository name:</b> fintech-review-analytics (GitHub)",
        "<b>Task 1:</b> complete on <font face='Courier'>task-1</font> branch — scraper, preprocessor, README, CI",
        "<b>Task 2:</b> in progress on <font face='Courier'>task-2</font> branch — sentiment module scaffolded; full DistilBERT run pending",
        "<b>CI:</b> GitHub Actions installs <font face='Courier'>requirements.txt</font> and runs pytest on push",
        "<b>Data policy:</b> CSV/JSON under <font face='Courier'>data/</font> excluded from Git per assignment",
    ], body))

    # 6. Blockers and plan
    s.append(Paragraph("6. Blockers and Plan for Final Submission", h1))
    s.append(Paragraph("<b>Blockers encountered</b>", h2))
    s.append(bullets([
        "<b>Large ML dependencies:</b> Installing PyTorch + Transformers locally was slow/interrupted on limited bandwidth; VADER used for interim findings.",
        "<b>Play Store rate limits:</b> Mitigated via batched requests and 0.5s delays; no shortage of reviews for the three apps.",
        "<b>Binary SST-2 model:</b> DistilBERT outputs positive/negative only; neutral class will use a confidence threshold (&lt;0.55) in final pipeline.",
    ], body))
    s.append(Paragraph("<b>Plan through final submission (19 May 2026)</b>", h2))
    s.append(bullets([
        "<b>Task 2 (complete):</b> Run DistilBERT sentiment; TF-IDF/spaCy thematic analysis (3–5 themes per bank); merge to task-2 → main.",
        "<b>Task 3:</b> PostgreSQL schema (banks, reviews); insert cleaned + enriched data; verification SQL.",
        "<b>Task 4:</b> 3–5 stakeholder plots; bank-specific drivers, pain points, and recommendations; final report (≤15 pages PDF).",
        "<b>Git:</b> Merge task-1 to main; open PRs for task-2/3/4; maintain conventional commits.",
    ], body))

    s.append(Spacer(1, 0.5 * cm))
    s.append(Paragraph(
        "<i>End of interim report (≤5 pages). Replace [Your Name] and attach GitHub link before submission.</i>",
        ParagraphStyle("foot", parent=small, alignment=TA_CENTER),
    ))
    return s


def main():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Week 2 Interim Report",
    )
    doc.build(build_story())
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()
