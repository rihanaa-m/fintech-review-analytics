# Fintech Review Analytics

Week 2 challenge: scrape and analyze Google Play Store reviews for Ethiopian bank mobile apps (CBE, BOA, Dashen).

## Repository layout

| Path | Role |
|------|------|
| `scripts/` | Scraping and preprocessing scripts |
| `notebooks/` | Exploratory analysis notebooks |
| `src/` | Reusable pipeline modules |
| `tests/` | Unit tests (CI) |
| `data/raw/` | Local scraped data (gitignored) |

## Environment setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
pip install --upgrade pip
pip install -r requirements.txt
```

## Git workflow

- **`main`**: stable branch with setup, CI, and merged task work
- **`task-1`**: data collection and preprocessing
- **`task-2`**: sentiment and thematic analysis (current)
- **`task-3`**, **`task-4`**: database and insights (merge via pull requests)

Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

## CI

GitHub Actions (`.github/workflows/unittests.yml`) installs dependencies on every push to `main` and runs `pytest`.

## Task 1 — Data collection and preprocessing

### Apps scraped

| Bank | Play Store app ID | Listing name |
|------|-------------------|--------------|
| CBE | `com.combanketh.mobilebanking` | Commercial Bank of Ethiopia |
| BOA | `com.boa.boaMobileBanking` | BoA Mobile |
| Dashen | `com.dashen.dashensuperapp` | Dashen Bank |

### Scraping methodology

- **Library:** [google-play-scraper](https://github.com/JoMingyu/google-play-scraper)
- **Country / language:** `et` / `en` (Ethiopia storefront, English reviews)
- **Sort order:** newest first (`Sort.NEWEST`)
- **Batch size:** 200 reviews per request, with continuation tokens until ≥400 per bank
- **Fields collected:** review text, rating (1–5), date, bank code, app name, source (`Google Play`), plus `review_id` for deduplication (dropped from final CSV)
- **Rate limiting:** 0.5s pause between paginated requests

### Run the pipeline

```bash
# 1) Scrape (writes data/raw/reviews_raw.json — gitignored)
python scripts/scrape_play_reviews.py

# 2) Clean and export CSV (data/raw/reviews_cleaned.csv — gitignored)
python scripts/preprocess_reviews.py
```

### Preprocessing rules

1. Remove duplicate reviews by `review_id`
2. Drop rows with missing review text or rating (counts printed to console)
3. Normalize dates to `YYYY-MM-DD`
4. Output columns: `review`, `rating`, `date`, `bank`, `source`

CSV and raw JSON files are listed in `.gitignore` and must not be pushed to GitHub.

## Task 2.1 — Sentiment analysis (interim)

### Model and rationale

- **Model:** `distilbert-base-uncased-finetuned-sst-2-english` (Hugging Face Transformers)
- **Why:** Strong accuracy on short English text; fits Play Store review length. SST-2 is binary (positive/negative); reviews with confidence below **0.55** are labeled **neutral**.
- **Output:** `sentiment_label` (positive / negative / neutral), `sentiment_score` (model confidence 0–1)

### Run sentiment + chart

```bash
# Requires Task 1 cleaned data locally
python scripts/run_sentiment_analysis.py
python scripts/plot_sentiment.py
```

**Outputs (local, gitignored under `data/processed/`):**

| File | Description |
|------|-------------|
| `sentiment_results.csv` | Per review: `review_id`, `review_text`, `sentiment_label`, `sentiment_score`, `identified_theme` |
| `sentiment_by_bank.csv` | Aggregated means and label % per bank |
| `sentiment_by_bank_rating.csv` | Mean sentiment by bank and star rating |

**Interim chart (committed):** `analysis_outputs/task2/sentiment_by_bank.png`
