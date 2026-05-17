"""Smoke tests for repository setup (CI)."""


def test_imports():
    import pandas  # noqa: F401
    import google_play_scraper  # noqa: F401


def test_project_layout():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    assert (root / "requirements.txt").is_file()
    assert (root / ".gitignore").is_file()
    assert (root / "README.md").is_file()
