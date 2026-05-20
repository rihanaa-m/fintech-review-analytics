"""Tests for thematic analysis."""

import pandas as pd

from src.themes import assign_theme, add_themes


def test_assign_theme_login():
    assert assign_theme("Cannot login, OTP not received") == "Account Access Issues"


def test_assign_theme_transfer():
    assert assign_theme("Very slow transfer and app keeps crashing") == "Transaction Performance"


def test_add_themes_column():
    df = pd.DataFrame({"review_text": ["Great UI, easy to use", "OTP failed again"]})
    out = add_themes(df)
    assert "identified_theme" in out.columns
    assert len(out["identified_theme"].unique()) >= 1
