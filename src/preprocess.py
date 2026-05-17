"""Review dataset cleaning for Task 1 preprocessing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

OUTPUT_COLUMNS = ("review", "rating", "date", "bank", "source")


@dataclass
class PreprocessReport:
    input_rows: int
    duplicates_removed: int
    dropped_missing_review: int
    dropped_missing_rating: int
    output_rows: int
    by_bank: dict[str, int]


def _parse_dates(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True).dt.tz_convert(None).dt.normalize()


def preprocess_reviews(df: pd.DataFrame) -> tuple[pd.DataFrame, PreprocessReport]:
    """
    Clean scraped reviews per assignment spec.

    - Drop duplicate review_id
    - Drop rows missing review text or rating
    - Normalize date to YYYY-MM-DD
    - Keep columns: review, rating, date, bank, source
    """
    work = df.copy()
    input_rows = len(work)

    if "review_id" in work.columns:
        before = len(work)
        work = work.drop_duplicates(subset=["review_id"], keep="first")
        duplicates_removed = before - len(work)
    else:
        duplicates_removed = 0

    work["review"] = work["review"].astype(str).str.strip()
    work["rating"] = pd.to_numeric(work["rating"], errors="coerce")

    missing_review_mask = work["review"].eq("") | work["review"].isna()
    dropped_missing_review = int(missing_review_mask.sum())
    work = work.loc[~missing_review_mask]

    missing_rating_mask = work["rating"].isna()
    dropped_missing_rating = int(missing_rating_mask.sum())
    work = work.loc[~missing_rating_mask]

    work["date"] = _parse_dates(work["date"]).dt.strftime("%Y-%m-%d")
    work = work.dropna(subset=["date"])

    for col in OUTPUT_COLUMNS:
        if col not in work.columns:
            raise ValueError(f"Missing required column: {col}")

    cleaned = work.loc[:, OUTPUT_COLUMNS].copy()
    cleaned["rating"] = cleaned["rating"].astype(int)
    cleaned = cleaned.sort_values(["bank", "date"]).reset_index(drop=True)

    by_bank = cleaned.groupby("bank").size().astype(int).to_dict()
    report = PreprocessReport(
        input_rows=input_rows,
        duplicates_removed=duplicates_removed,
        dropped_missing_review=dropped_missing_review,
        dropped_missing_rating=dropped_missing_rating,
        output_rows=len(cleaned),
        by_bank=by_bank,
    )
    return cleaned, report


def records_to_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Build a DataFrame from scraped JSON records."""
    return pd.DataFrame(records)
