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
- **`task-2`**, **`task-3`**, **`task-4`**: later tasks (merge via pull requests)

Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

## CI

GitHub Actions (`.github/workflows/unittests.yml`) installs dependencies on every push to `main` and runs `pytest`.

## Task 1 (in progress)

Scrape 400+ reviews per bank from Google Play, preprocess to CSV (`review`, `rating`, `date`, `bank`, `source`), and keep data files out of version control.
