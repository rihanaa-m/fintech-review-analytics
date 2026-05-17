"""
Scrape Google Play Store reviews for CBE, BOA, and Dashen bank apps.

Usage:
    python scripts/scrape_play_reviews.py
    python scripts/scrape_play_reviews.py --target 500 --output data/raw/reviews_raw.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.apps import BANK_APPS, MIN_REVIEWS_PER_BANK
from src.scraper import save_raw_json, scrape_all_banks


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Google Play reviews for bank apps.")
    parser.add_argument(
        "--target",
        type=int,
        default=MIN_REVIEWS_PER_BANK,
        help=f"Minimum reviews per bank (default: {MIN_REVIEWS_PER_BANK})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "raw" / "reviews_raw.json",
        help="Path for raw JSON output",
    )
    parser.add_argument("--country", default="et", help="Play Store country code (default: et)")
    parser.add_argument("--lang", default="en", help="Review language (default: en)")
    args = parser.parse_args()

    print(f"Scraping {len(BANK_APPS)} apps (target {args.target} reviews each)...")
    records = scrape_all_banks(
        target_per_bank=args.target,
        lang=args.lang,
        country=args.country,
    )

    counts: dict[str, int] = {}
    for record in records:
        counts[record["bank"]] = counts.get(record["bank"], 0) + 1

    save_raw_json(records, args.output)
    print(f"Saved {len(records)} raw reviews -> {args.output}")
    for bank_app in BANK_APPS:
        n = counts.get(bank_app.bank, 0)
        status = "OK" if n >= args.target else "BELOW TARGET"
        print(f"  {bank_app.bank}: {n} reviews [{status}]")


if __name__ == "__main__":
    main()
