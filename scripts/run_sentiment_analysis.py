"""
Run DistilBERT sentiment analysis on cleaned bank reviews (Task 2.1).

Usage:
    python scripts/run_sentiment_analysis.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.sentiment import (
    MODEL_NAME,
    aggregate_by_bank,
    aggregate_by_bank_and_rating,
    load_reviews_with_ids,
    run_sentiment_analysis,
    to_output_frame,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify review sentiment with DistilBERT.")
    parser.add_argument(
        "--cleaned",
        type=Path,
        default=ROOT / "data" / "raw" / "reviews_cleaned.csv",
    )
    parser.add_argument(
        "--raw",
        type=Path,
        default=ROOT / "data" / "raw" / "reviews_raw.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "processed" / "sentiment_results.csv",
    )
    parser.add_argument(
        "--summary-bank",
        type=Path,
        default=ROOT / "data" / "processed" / "sentiment_by_bank.csv",
    )
    parser.add_argument(
        "--summary-rating",
        type=Path,
        default=ROOT / "data" / "processed" / "sentiment_by_bank_rating.csv",
    )
    args = parser.parse_args()

    if not args.cleaned.is_file():
        raise SystemExit(f"Missing cleaned data: {args.cleaned}. Complete Task 1 first.")
    if not args.raw.is_file():
        raise SystemExit(f"Missing raw data: {args.raw}. Run scrape_play_reviews.py first.")

    print(f"Loading reviews (model: {MODEL_NAME})...")
    df = load_reviews_with_ids(args.cleaned, args.raw)
    print(f"Classifying {len(df)} reviews...")
    analyzed = run_sentiment_analysis(df)

    output = to_output_frame(analyzed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False, encoding="utf-8")

    by_bank = aggregate_by_bank(analyzed)
    by_rating = aggregate_by_bank_and_rating(analyzed)
    by_bank.to_csv(args.summary_bank, index=False)
    by_rating.to_csv(args.summary_rating, index=False)

    print(f"Saved per-review results -> {args.output}")
    print(f"Saved bank summary      -> {args.summary_bank}")
    print(f"Saved bank×rating summary -> {args.summary_rating}")
    print("\nSentiment distribution (%):")
    print(
        analyzed.groupby(["bank", "sentiment_label"])
        .size()
        .unstack(fill_value=0)
        .div(analyzed.groupby("bank").size(), axis=0)
        .mul(100)
        .round(1)
    )


if __name__ == "__main__":
    main()
