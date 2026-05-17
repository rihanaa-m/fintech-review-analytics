"""
Plot sentiment distribution by bank (Task 2.1 — interim visualization).

Usage:
    python scripts/plot_sentiment.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def plot_sentiment_by_bank(df: pd.DataFrame, output_path: Path) -> None:
    """Stacked bar chart: share of positive / negative / neutral per bank."""
    counts = (
        df.groupby(["bank", "sentiment_label"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["positive", "neutral", "negative"], fill_value=0)
    )
    pct = counts.div(counts.sum(axis=1), axis=0) * 100

    sns.set_theme(style="whitegrid", font_scale=1.05)
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = {"positive": "#2f855a", "neutral": "#718096", "negative": "#c53030"}
    bottom = pd.Series(0.0, index=pct.index)
    for label in ["positive", "neutral", "negative"]:
        ax.bar(pct.index, pct[label], bottom=bottom, label=label.capitalize(), color=colors[label])
        bottom = bottom + pct[label]

    ax.set_ylabel("Share of reviews (%)")
    ax.set_xlabel("Bank")
    ax.set_title("Sentiment distribution by bank (DistilBERT SST-2)")
    ax.legend(title="Sentiment", loc="upper right")
    ax.set_ylim(0, 100)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot sentiment charts for interim report.")
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "processed" / "sentiment_results.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "analysis_outputs" / "task2" / "sentiment_by_bank.png",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"Missing {args.input}. Run scripts/run_sentiment_analysis.py first.")

    df = pd.read_csv(args.input)
    plot_sentiment_by_bank(df, args.output)
    print(f"Saved chart -> {args.output}")


if __name__ == "__main__":
    main()
