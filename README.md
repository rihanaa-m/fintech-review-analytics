# Fintech Review Analytics

Week 2 challenge: scrape and analyze Google Play Store reviews for Ethiopian bank mobile apps (CBE, BOA, Dashen).

## Repository layout

| Path | Role |
|------|------|
| `scripts/` | CLI pipelines (scrape, preprocess, sentiment, themes, DB, plots, reports) |
| `src/` | Reusable modules |
| `database/schema.sql` | PostgreSQL DDL |
| `tests/` | Pytest (CI) |
| `analysis_outputs/` | Committed charts for reports |
| `data/raw/`, `data/processed/` | Local data (gitignored) |

## Environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Full pipeline (Tasks 1–4)

```bash
# Task 1
python scripts/scrape_play_reviews.py
python scripts/preprocess_reviews.py

# Task 2
python scripts/run_sentiment_analysis.py
python scripts/run_thematic_analysis.py

# Task 4 visuals
python scripts/plot_sentiment.py
python scripts/generate_insights.py

# Task 3 (PostgreSQL must be running)
set DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/bank_reviews
createdb bank_reviews
python scripts/load_to_postgres.py

# Reports
python scripts/generate_final_report_pdf.py
```

Or run Tasks 2–4 data steps in one command:

```bash
python scripts/run_full_pipeline.py
python scripts/run_full_pipeline.py --load-db
```

## Apps

| Bank | App ID |
|------|--------|
| CBE | `com.combanketh.mobilebanking` |
| BOA | `com.boa.boaMobileBanking` |
| Dashen | `com.dashen.dashensuperapp` |

## Task 1 — Scrape & preprocess

- ≥400 reviews per bank via `google-play-scraper` (country `et`, sort NEWEST)
- Output: `data/raw/reviews_cleaned.csv` (columns: review, rating, date, bank, source)

## Task 2 — Sentiment & themes

- **Sentiment:** DistilBERT SST-2; confidence &lt; 0.55 → neutral
- **Themes:** keyword rules + TF-IDF keywords per bank
- Output: `data/processed/reviews_analyzed.csv`

## Task 3 — PostgreSQL

1. Install PostgreSQL and create database `bank_reviews`
2. Apply `database/schema.sql` or let `load_to_postgres.py` create tables
3. Set `DATABASE_URL` and run `python scripts/load_to_postgres.py`
4. Verification JSON: `data/processed/db_verification.json`

## Task 4 — Insights

Plots in `analysis_outputs/task4/` (sentiment, ratings, themes, trends, keywords).  
Recommendations JSON: `analysis_outputs/task4/recommendations.json`

## Git branches

- `task-1` → scrape/preprocess → merge to `main`
- `task-2` → sentiment/themes → merge to `main`
- `task-3` → database → merge to `main`
- `task-4` → insights + final report → merge to `main`

## CI

GitHub Actions runs `pytest` on push (no model download in tests).

## Submission

- **GitHub:** `main` with all tasks merged
- **PDF:** `Week_2_Final_Report.pdf` (generate locally, upload to Drive)
