"""
Preprocess scraped Play Store reviews into a clean CSV.

Usage:
    python scripts/preprocess_reviews.py
    python scripts/preprocess_reviews.py --input data/raw/reviews_raw.json --output data/raw/reviews_cleaned.csv
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

from src.preprocess import preprocess_reviews, records_to_dataframe


def load_raw_json(path: Path) -> pd.DataFrame:
    with path.open(encoding="utf-8") as f:
        records = json.load(f)
    return records_to_dataframe(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean scraped bank app reviews.")
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "raw" / "reviews_raw.json",
        help="Raw JSON from scrape_play_reviews.py",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "raw" / "reviews_cleaned.csv",
        help="Cleaned CSV output path",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"Input not found: {args.input}. Run scripts/scrape_play_reviews.py first.")

    df = load_raw_json(args.input)
    cleaned, report = preprocess_reviews(df)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(args.output, index=False, encoding="utf-8")

    print(f"Input rows:            {report.input_rows}")
    print(f"Duplicates removed:  {report.duplicates_removed}")
    print(f"Dropped (no review): {report.dropped_missing_review}")
    print(f"Dropped (no rating): {report.dropped_missing_rating}")
    print(f"Output rows:         {report.output_rows}")
    print("Per bank:")
    for bank, count in sorted(report.by_bank.items()):
        print(f"  {bank}: {count}")
    print(f"Saved -> {args.output}")


if __name__ == "__main__":
    main()
