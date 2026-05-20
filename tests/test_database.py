"""Database tests using SQLite in-memory (CI-friendly)."""

import pandas as pd
from sqlalchemy import create_engine, text

from src.database import init_schema, load_reviews, seed_banks


def test_load_reviews_sqlite():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE banks (
                    bank_id INTEGER PRIMARY KEY,
                    bank_name VARCHAR(100) UNIQUE,
                    app_name VARCHAR(200)
                );
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE reviews (
                    review_id VARCHAR(64) PRIMARY KEY,
                    bank_id INTEGER,
                    review_text TEXT,
                    rating INTEGER,
                    review_date DATE,
                    sentiment_label VARCHAR(20),
                    sentiment_score REAL,
                    identified_theme VARCHAR(100),
                    source VARCHAR(50)
                );
                """
            )
        )
        conn.execute(
            text("INSERT INTO banks (bank_id, bank_name, app_name) VALUES (1,'CBE','CBE App')")
        )

    df = pd.DataFrame(
        [
            {
                "review_id": "r1",
                "bank": "CBE",
                "review_text": "Good app",
                "rating": 5,
                "date": "2025-01-01",
                "sentiment_label": "positive",
                "sentiment_score": 0.9,
                "identified_theme": "UI & Design",
            }
        ]
    )
    n = load_reviews(engine, df)
    assert n == 1
