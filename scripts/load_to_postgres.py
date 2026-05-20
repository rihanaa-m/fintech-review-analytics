"""
Load analyzed reviews into PostgreSQL (Task 3).

Set DATABASE_URL, e.g.:
  postgresql+psycopg2://postgres:yourpassword@localhost:5432/bank_reviews

Create DB first:
  createdb bank_reviews

Usage:
    python scripts/load_to_postgres.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from src.database import (
    get_engine,
    init_schema,
    load_reviews,
    run_verification_queries,
    seed_banks,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load reviews into PostgreSQL.")
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "processed" / "reviews_analyzed_full.csv",
    )
    parser.add_argument(
        "--verify-out",
        type=Path,
        default=ROOT / "data" / "processed" / "db_verification.json",
    )
    parser.add_argument("--database-url", default=None, help="Override DATABASE_URL")
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"Missing {args.input}. Run Task 2 pipeline first.")

    df = pd.read_csv(args.input)
    if "rating" not in df.columns and "review_text" in df.columns:
        pass
    # merge rating/date from cleaned if missing
    cleaned_path = ROOT / "data" / "raw" / "reviews_cleaned.csv"
    if cleaned_path.is_file() and "rating" not in df.columns:
        cleaned = pd.read_csv(cleaned_path).rename(columns={"review": "review_text"})
        df = df.merge(cleaned[["review_text", "rating", "date", "bank"]], on=["review_text", "bank"], how="left")

    engine = get_engine(args.database_url)
    print("Initializing schema...")
    init_schema(engine)
    seed_banks(engine)
    n = load_reviews(engine, df)
    print(f"Inserted {n} reviews.")

    verification = run_verification_queries(engine)
    args.verify_out.parent.mkdir(parents=True, exist_ok=True)
    args.verify_out.write_text(json.dumps(verification, indent=2), encoding="utf-8")
    print(f"Verification saved -> {args.verify_out}")
    for key, value in verification.items():
        print(f"\n{key}:")
        print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
