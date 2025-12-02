"""Compute VADER sentiment for cleaned reviews and persist to CSV.

Usage:
    python scripts/add_vader_sentiment.py

This will add columns `vader` (float) and `sentiment_label` ('pos'/'neu'/'neg') to
`data/processed/reviews_clean.csv` in-place.
"""
from pathlib import Path
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def label_from_score(s: float) -> str:
    if s >= 0.05:
        return "pos"
    if s <= -0.05:
        return "neg"
    return "neu"


def main():
    path = Path("data/processed/reviews_clean.csv")
    if not path.exists():
        print("Cleaned CSV not found at", path)
        return
    df = pd.read_csv(path)
    analyzer = SentimentIntensityAnalyzer()
    print("Computing VADER sentiment for", len(df), "rows")
    df["vader"] = df["review"].astype(str).apply(lambda t: analyzer.polarity_scores(t)["compound"])
    df["sentiment_label"] = df["vader"].apply(label_from_score)
    df.to_csv(path, index=False)
    print("Persisted vader + sentiment_label to", path)


if __name__ == "__main__":
    main()
