"""PostgreSQL load helpers for Task 3."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.apps import BANK_APPS

DEFAULT_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/bank_reviews"


def get_engine(url: str | None = None) -> Engine:
    db_url = url or os.environ.get("DATABASE_URL", DEFAULT_URL)
    return create_engine(db_url)


def init_schema(engine: Engine) -> None:
    """Create banks and reviews tables if they do not exist."""
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS banks (
                    bank_id SERIAL PRIMARY KEY,
                    bank_name VARCHAR(100) NOT NULL UNIQUE,
                    app_name VARCHAR(200) NOT NULL
                );
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS reviews (
                    review_id VARCHAR(64) PRIMARY KEY,
                    bank_id INTEGER NOT NULL REFERENCES banks(bank_id),
                    review_text TEXT NOT NULL,
                    rating SMALLINT NOT NULL,
                    review_date DATE NOT NULL,
                    sentiment_label VARCHAR(20),
                    sentiment_score NUMERIC(6, 4),
                    identified_theme VARCHAR(100),
                    source VARCHAR(50) DEFAULT 'Google Play'
                );
                """
            )
        )


def seed_banks(engine: Engine) -> None:
    with engine.begin() as conn:
        for app in BANK_APPS:
            conn.execute(
                text(
                    """
                    INSERT INTO banks (bank_name, app_name)
                    VALUES (:bank_name, :app_name)
                    ON CONFLICT (bank_name) DO NOTHING;
                    """
                ),
                {"bank_name": app.bank, "app_name": app.display_name},
            )


def load_reviews(engine: Engine, df: pd.DataFrame) -> int:
    """Insert analyzed reviews; returns rows inserted."""
    bank_map = pd.read_sql("SELECT bank_id, bank_name FROM banks", engine)
    name_to_id = dict(zip(bank_map["bank_name"], bank_map["bank_id"]))

    work = df.copy()
    work["bank_id"] = work["bank"].map(name_to_id)
    work = work.dropna(subset=["bank_id"])
    work["bank_id"] = work["bank_id"].astype(int)

    insert_df = work[
        [
            "review_id",
            "bank_id",
            "review_text",
            "rating",
            "date",
            "sentiment_label",
            "sentiment_score",
            "identified_theme",
        ]
    ].rename(columns={"date": "review_date"})
    insert_df["source"] = "Google Play"

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM reviews"))
        insert_df.to_sql("reviews", conn, if_exists="append", index=False)

    return len(insert_df)


def run_verification_queries(engine: Engine) -> dict:
    """Return verification stats for README/report."""
    queries = {
        "reviews_per_bank": """
            SELECT b.bank_name, COUNT(r.review_id) AS review_count
            FROM banks b
            LEFT JOIN reviews r ON b.bank_id = r.bank_id
            GROUP BY b.bank_name ORDER BY b.bank_name;
        """,
        "avg_rating_per_bank": """
            SELECT b.bank_name, ROUND(AVG(r.rating)::numeric, 2) AS avg_rating
            FROM banks b
            JOIN reviews r ON b.bank_id = r.bank_id
            GROUP BY b.bank_name ORDER BY b.bank_name;
        """,
        "null_check": """
            SELECT COUNT(*) AS null_sentiment
            FROM reviews
            WHERE sentiment_label IS NULL OR sentiment_score IS NULL;
        """,
    }
    results = {}
    with engine.connect() as conn:
        for name, sql in queries.items():
            results[name] = pd.read_sql(text(sql), conn).to_dict(orient="records")
    return results
