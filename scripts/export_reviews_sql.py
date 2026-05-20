"""Export INSERT statements for reviews (Task 3 backup without live DB)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.apps import BANK_APPS

INPUT = ROOT / "data" / "processed" / "reviews_analyzed_full.csv"
OUTPUT = ROOT / "database" / "seed_reviews.sql"


def esc(val) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(f"Run Task 2 pipeline first. Missing {INPUT}")

    df = pd.read_csv(INPUT)
    lines = ["-- Generated seed SQL for bank_reviews", "BEGIN;", ""]

    for app in BANK_APPS:
        lines.append(
            f"INSERT INTO banks (bank_name, app_name) VALUES ({esc(app.bank)}, {esc(app.display_name)}) "
            f"ON CONFLICT (bank_name) DO NOTHING;"
        )
    lines.append("")

    for _, row in df.iterrows():
        lines.append(
            "INSERT INTO reviews (review_id, bank_id, review_text, rating, review_date, "
            "sentiment_label, sentiment_score, identified_theme, source) "
            f"SELECT {esc(row['review_id'])}, bank_id, {esc(row['review_text'])}, "
            f"{int(row['rating'])}, {esc(row['date'])}, {esc(row['sentiment_label'])}, "
            f"{float(row['sentiment_score']):.4f}, {esc(row['identified_theme'])}, 'Google Play' "
            f"FROM banks WHERE bank_name = {esc(row['bank'])} "
            "ON CONFLICT (review_id) DO NOTHING;"
        )

    lines.append("COMMIT;")
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(df)} review inserts -> {OUTPUT}")


if __name__ == "__main__":
    main()
