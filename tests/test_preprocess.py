"""Unit tests for review preprocessing (no live scraping)."""

import pandas as pd

from src.preprocess import OUTPUT_COLUMNS, preprocess_reviews


def test_preprocess_dedup_and_columns():
    df = pd.DataFrame(
        [
            {
                "review_id": "a1",
                "review": "  Fast transfers  ",
                "rating": 5,
                "date": "2024-06-01T10:00:00",
                "bank": "CBE",
                "source": "Google Play",
            },
            {
                "review_id": "a1",
                "review": "duplicate",
                "rating": 4,
                "date": "2024-06-02",
                "bank": "CBE",
                "source": "Google Play",
            },
            {
                "review_id": "a2",
                "review": "",
                "rating": 3,
                "date": "2024-06-03",
                "bank": "BOA",
                "source": "Google Play",
            },
            {
                "review_id": "a3",
                "review": "App crashes",
                "rating": None,
                "date": "2024-06-04",
                "bank": "Dashen",
                "source": "Google Play",
            },
        ]
    )

    cleaned, report = preprocess_reviews(df)

    assert list(cleaned.columns) == list(OUTPUT_COLUMNS)
    assert report.input_rows == 4
    assert report.duplicates_removed == 1
    assert report.dropped_missing_review == 1
    assert report.dropped_missing_rating == 1
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["review"] == "Fast transfers"
    assert cleaned.iloc[0]["rating"] == 5
    assert cleaned.iloc[0]["date"] == "2024-06-01"
