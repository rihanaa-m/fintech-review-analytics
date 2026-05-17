"""Sentiment classification for bank app reviews (Task 2.1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import pandas as pd

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
NEUTRAL_CONFIDENCE_THRESHOLD = 0.55
BATCH_SIZE = 32

SENTIMENT_COLUMNS = (
    "review_id",
    "review_text",
    "sentiment_label",
    "sentiment_score",
    "identified_theme",
)


@dataclass(frozen=True)
class SentimentPrediction:
    label: str
    confidence: float
    signed_score: float


def map_binary_to_three_way(label: str, confidence: float) -> SentimentPrediction:
    """
    Map DistilBERT SST-2 output (POSITIVE/NEGATIVE) to positive/negative/neutral.

    Low-confidence predictions are treated as neutral for business readability.
    signed_score: +confidence (positive), -confidence (negative), 0.0 (neutral).
    """
    label_upper = label.upper()
    if confidence < NEUTRAL_CONFIDENCE_THRESHOLD:
        return SentimentPrediction("neutral", confidence, 0.0)
    if label_upper == "POSITIVE":
        return SentimentPrediction("positive", confidence, confidence)
    if label_upper == "NEGATIVE":
        return SentimentPrediction("negative", confidence, -confidence)
    return SentimentPrediction("neutral", confidence, 0.0)


def build_classifier(model_name: str = MODEL_NAME):
    """Load Hugging Face sentiment pipeline (downloads model on first use)."""
    from transformers import pipeline

    return pipeline(
        "sentiment-analysis",
        model=model_name,
        truncation=True,
        max_length=512,
    )


def classify_texts(
    texts: Sequence[str],
    classifier=None,
    batch_size: int = BATCH_SIZE,
) -> list[SentimentPrediction]:
    """Classify a list of review texts in batches."""
    if classifier is None:
        classifier = build_classifier()

    predictions: list[SentimentPrediction] = []
    for start in range(0, len(texts), batch_size):
        batch = list(texts[start : start + batch_size])
        results = classifier(batch)
        if isinstance(results, dict):
            results = [results]
        for item in results:
            predictions.append(map_binary_to_three_way(item["label"], float(item["score"])))
    return predictions


def load_reviews_with_ids(
    cleaned_path: str | pd.PathLike,
    raw_json_path: str | pd.PathLike,
) -> pd.DataFrame:
    """Merge cleaned reviews with review_id from raw scrape JSON."""
    cleaned = pd.read_csv(cleaned_path).rename(columns={"review": "review_text"})
    raw = pd.read_json(raw_json_path).rename(columns={"review": "review_text"})

    merge_cols = ["review_text", "rating", "date", "bank"]
    merged = cleaned.merge(
        raw[["review_id", *merge_cols]],
        on=merge_cols,
        how="left",
    )
    missing = merged["review_id"].isna()
    if missing.any():
        merged.loc[missing, "review_id"] = "gen-" + merged.index[missing].astype(str)
    return merged


def run_sentiment_analysis(
    df: pd.DataFrame,
    classifier=None,
    text_column: str = "review_text",
) -> pd.DataFrame:
    """Add sentiment_label and sentiment_score to review rows."""
    texts = df[text_column].astype(str).tolist()
    preds = classify_texts(texts, classifier=classifier)

    out = df.copy()
    out["sentiment_label"] = [p.label for p in preds]
    out["sentiment_score"] = [p.confidence for p in preds]
    out["signed_sentiment"] = [p.signed_score for p in preds]
    if "identified_theme" not in out.columns:
        out["identified_theme"] = ""
    return out


def to_output_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Select Task 2 pipeline columns."""
    work = df.copy()
    if "review_text" not in work.columns and "review" in work.columns:
        work = work.rename(columns={"review": "review_text"})
    return work.loc[:, list(SENTIMENT_COLUMNS)].copy()


def aggregate_by_bank(df: pd.DataFrame) -> pd.DataFrame:
    """Mean confidence and label shares per bank."""
    rows = []
    for bank, group in df.groupby("bank"):
        label_counts = group["sentiment_label"].value_counts(normalize=True).mul(100).round(2)
        rows.append(
            {
                "bank": bank,
                "review_count": len(group),
                "mean_sentiment_score": round(group["sentiment_score"].mean(), 4),
                "mean_signed_sentiment": round(group["signed_sentiment"].mean(), 4),
                "pct_positive": label_counts.get("positive", 0.0),
                "pct_negative": label_counts.get("negative", 0.0),
                "pct_neutral": label_counts.get("neutral", 0.0),
            }
        )
    return pd.DataFrame(rows)


def aggregate_by_bank_and_rating(df: pd.DataFrame) -> pd.DataFrame:
    """Mean sentiment score per bank and star rating."""
    agg = (
        df.groupby(["bank", "rating"])
        .agg(
            review_count=("sentiment_score", "size"),
            mean_sentiment_score=("sentiment_score", "mean"),
            mean_signed_sentiment=("signed_sentiment", "mean"),
        )
        .reset_index()
    )
    agg["mean_sentiment_score"] = agg["mean_sentiment_score"].round(4)
    agg["mean_signed_sentiment"] = agg["mean_signed_sentiment"].round(4)
    return agg
