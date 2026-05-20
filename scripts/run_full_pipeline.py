"""
Run Week 2 analysis pipeline end-to-end (Tasks 2–4 data steps).

Usage:
    python scripts/run_full_pipeline.py
    python scripts/run_full_pipeline.py --skip-sentiment   # if already run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str, extra: list[str] | None = None) -> None:
    cmd = [sys.executable, str(ROOT / "scripts" / script)] + (extra or [])
    print(f"\n>>> {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-sentiment", action="store_true")
    parser.add_argument("--skip-scrape", action="store_true")
    parser.add_argument("--load-db", action="store_true", help="Also run PostgreSQL load")
    args = parser.parse_args()

    if not args.skip_scrape:
        cleaned = ROOT / "data" / "raw" / "reviews_cleaned.csv"
        if not cleaned.is_file():
            run("scrape_play_reviews.py")
            run("preprocess_reviews.py")

    if not args.skip_sentiment:
        run("run_sentiment_analysis.py")
    run("run_thematic_analysis.py")
    run("plot_sentiment.py")
    run("generate_insights.py")

    if args.load_db:
        run("load_to_postgres.py")

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
