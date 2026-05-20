"""Thematic analysis: TF-IDF keywords + rule-based theme assignment."""

from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Business themes from Week 2 brief
THEMES: tuple[str, ...] = (
    "Account Access Issues",
    "Transaction Performance",
    "UI & Design",
    "Customer Support",
    "Feature Requests",
)

THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Account Access Issues": (
        "login", "log in", "sign in", "password", "otp", "pin", "locked", "access",
        "verify", "authentication", "account",
    ),
    "Transaction Performance": (
        "slow", "transfer", "loading", "load", "crash", "freeze", "lag", "delay",
        "timeout", "failed", "error", "payment", "transaction", "speed",
    ),
    "UI & Design": (
        "ui", "interface", "design", "layout", "easy", "simple", "navigate",
        "screen", "look", "beautiful", "clean",
    ),
    "Customer Support": (
        "support", "service", "call", "help", "agent", "branch", "complaint",
        "response", "customer",
    ),
    "Feature Requests": (
        "feature", "add", "wish", "need", "want", "fingerprint", "budget",
        "notification", "update", "improve", "request",
    ),
}

TOKEN_PATTERN = re.compile(r"[a-zA-Z']+")


def normalize_text(text: str) -> str:
    return " ".join(TOKEN_PATTERN.findall(str(text).lower()))


def assign_theme(text: str) -> str:
    """Pick theme with most keyword hits; default to UI & Design if tie/zero."""
    normalized = normalize_text(text)
    if not normalized:
        return "UI & Design"

    scores = {theme: 0 for theme in THEMES}
    for theme, keywords in THEME_KEYWORDS.items():
        for kw in keywords:
            if kw in normalized:
                scores[theme] += 1

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "UI & Design"
    return best


def add_themes(df: pd.DataFrame, text_column: str = "review_text") -> pd.DataFrame:
    """Add identified_theme column via keyword rules."""
    out = df.copy()
    out["identified_theme"] = out[text_column].astype(str).map(assign_theme)
    return out


@dataclass
class ThemeReport:
    bank: str
    theme: str
    count: int
    pct: float


def theme_summary_by_bank(df: pd.DataFrame) -> pd.DataFrame:
    """Count and percentage of each theme per bank."""
    rows: list[dict] = []
    for bank, group in df.groupby("bank"):
        total = len(group)
        for theme, count in group["identified_theme"].value_counts().items():
            rows.append(
                {
                    "bank": bank,
                    "theme": theme,
                    "count": int(count),
                    "pct": round(100 * count / total, 2),
                }
            )
    return pd.DataFrame(rows).sort_values(["bank", "count"], ascending=[True, False])


def top_keywords_per_bank(
    df: pd.DataFrame,
    text_column: str = "review_text",
    top_n: int = 15,
) -> dict[str, list[tuple[str, float]]]:
    """TF-IDF top terms per bank (unigrams + bigrams)."""
    result: dict[str, list[tuple[str, float]]] = {}
    for bank, group in df.groupby("bank"):
        texts = group[text_column].astype(str).map(normalize_text).tolist()
        if not texts:
            result[bank] = []
            continue
        vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=2,
        )
        try:
            matrix = vectorizer.fit_transform(texts)
        except ValueError:
            result[bank] = []
            continue
        scores = matrix.sum(axis=0).A1
        terms = vectorizer.get_feature_names_out()
        ranked = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)[:top_n]
        result[bank] = [(t, float(s)) for t, s in ranked]
    return result
