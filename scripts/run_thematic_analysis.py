"""
Apply thematic labels to sentiment results (Task 2.2).

Usage:
    python scripts/run_thematic_analysis.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.themes import add_themes, theme_summary_by_bank, top_keywords_per_bank


def main() -> None:
    parser = argparse.ArgumentParser(description="Assign themes to analyzed reviews.")
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "processed" / "sentiment_results.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "processed" / "reviews_analyzed_full.csv",
    )
    parser.add_argument(
        "--themes-summary",
        type=Path,
        default=ROOT / "data" / "processed" / "themes_by_bank.csv",
    )
    parser.add_argument(
        "--keywords-json",
        type=Path,
        default=ROOT / "data" / "processed" / "top_keywords_by_bank.json",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"Missing {args.input}. Run scripts/run_sentiment_analysis.py first.")

    df = pd.read_csv(args.input)
    raw_path = ROOT / "data" / "raw" / "reviews_raw.json"
    if raw_path.is_file() and "review_id" in df.columns:
        raw = pd.read_json(raw_path)[
            ["review_id", "rating", "date", "bank", "source"]
        ].drop_duplicates(subset=["review_id"])
        raw["date"] = pd.to_datetime(raw["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        df = df.merge(raw, on="review_id", how="left", suffixes=("", "_raw"))
    df = add_themes(df)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8")

    slim = df[
        ["review_id", "review_text", "sentiment_label", "sentiment_score", "identified_theme"]
    ]
    slim.to_csv(args.output.parent / "reviews_analyzed.csv", index=False, encoding="utf-8")

    summary = theme_summary_by_bank(df)
    summary.to_csv(args.themes_summary, index=False)

    keywords = top_keywords_per_bank(df)
    args.keywords_json.write_text(json.dumps(keywords, indent=2), encoding="utf-8")

    print(f"Saved analyzed reviews -> {args.output}")
    print(f"Saved theme summary   -> {args.themes_summary}")
    print(f"Saved top keywords    -> {args.keywords_json}")
    print("\nTheme counts per bank:")
    print(summary.pivot_table(index="bank", columns="theme", values="count", fill_value=0))


if __name__ == "__main__":
    main()
