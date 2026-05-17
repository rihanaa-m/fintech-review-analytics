"""Google Play Store review scraping."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from google_play_scraper import Sort, app, reviews

from src.apps import BANK_APPS, MIN_REVIEWS_PER_BANK, SOURCE_LABEL, BankApp

BATCH_SIZE = 200
DEFAULT_COUNTRY = "et"
DEFAULT_LANG = "en"
REQUEST_DELAY_SEC = 0.5


def fetch_app_title(app_id: str, lang: str = DEFAULT_LANG, country: str = DEFAULT_COUNTRY) -> str:
    """Return the Play Store listing title for an app."""
    result = app(app_id, lang=lang, country=country)
    return result["title"]


def scrape_app_reviews(
    bank_app: BankApp,
    *,
    target_count: int = MIN_REVIEWS_PER_BANK,
    lang: str = DEFAULT_LANG,
    country: str = DEFAULT_COUNTRY,
    sort: Sort = Sort.NEWEST,
) -> list[dict[str, Any]]:
    """
    Scrape reviews for one app until ``target_count`` is reached or Play Store has no more.

    Returns raw review dicts from google-play-scraper (includes reviewId, content, score, at).
    """
    collected: list[dict[str, Any]] = []
    continuation_token = None

    while len(collected) < target_count:
        batch, continuation_token = reviews(
            bank_app.app_id,
            lang=lang,
            country=country,
            sort=sort,
            count=BATCH_SIZE,
            continuation_token=continuation_token,
        )
        if not batch:
            break
        collected.extend(batch)
        if continuation_token is None:
            break
        time.sleep(REQUEST_DELAY_SEC)

    return collected[:target_count] if len(collected) > target_count else collected


def raw_review_to_record(review: dict[str, Any], bank_app: BankApp, app_title: str) -> dict[str, Any]:
    """Normalize a scraper review dict for downstream preprocessing."""
    return {
        "review_id": review["reviewId"],
        "review": (review.get("content") or "").strip(),
        "rating": review.get("score"),
        "date": review.get("at"),
        "bank": bank_app.bank,
        "app_name": app_title,
        "source": SOURCE_LABEL,
    }


def scrape_all_banks(
    *,
    target_per_bank: int = MIN_REVIEWS_PER_BANK,
    lang: str = DEFAULT_LANG,
    country: str = DEFAULT_COUNTRY,
) -> list[dict[str, Any]]:
    """Scrape all configured bank apps and return combined raw records."""
    all_records: list[dict[str, Any]] = []

    for bank_app in BANK_APPS:
        app_title = fetch_app_title(bank_app.app_id, lang=lang, country=country)
        raw = scrape_app_reviews(
            bank_app,
            target_count=target_per_bank,
            lang=lang,
            country=country,
        )
        for item in raw:
            all_records.append(raw_review_to_record(item, bank_app, app_title))
        time.sleep(REQUEST_DELAY_SEC)

    return all_records


def save_raw_json(records: list[dict[str, Any]], path: Path) -> None:
    """Persist raw scraped records (dates serialized as ISO strings)."""
    path.parent.mkdir(parents=True, exist_ok=True)

    def _serialize(obj: Any) -> Any:
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    with path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=_serialize)
