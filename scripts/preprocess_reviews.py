"""Preprocess raw review CSVs and produce a cleaned combined CSV.

Usage:
    python scripts/preprocess_reviews.py

Output:
    data/processed/reviews_clean.csv
"""
from pathlib import Path
import pandas as pd
from dateutil import parser


RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_FILE = OUT_DIR / "reviews_clean.csv"


def normalize_date(val):
    if pd.isna(val) or val == "":
        return None
    try:
        dt = parser.isoparse(val) if isinstance(val, str) else val
        return dt.date().isoformat()
    except Exception:
        try:
            dt = parser.parse(val)
            return dt.date().isoformat()
        except Exception:
            return None


def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = list(RAW_DIR.glob("raw_*.csv"))
    if not files:
        print("No raw CSV files found in data/raw/. Run the scraper first.")
        return

    dfs = []
    for f in files:
        df = pd.read_csv(f)
        # Ensure expected columns
        for col in ["content", "score", "at"]:
            if col not in df.columns:
                df[col] = None
        df = df.rename(columns={"content": "review", "score": "rating", "at": "date"})
        df["bank"] = df.get("bank") if "bank" in df.columns else f.stem.replace("raw_", "")
        df["source"] = df.get("source") if "source" in df.columns else "google_play"
        dfs.append(df[["review", "rating", "date", "bank", "source"]])

    combined = pd.concat(dfs, ignore_index=True)

    # Drop duplicates based on review text
    combined["review"] = combined["review"].astype(str)
    combined = combined.drop_duplicates(subset=["review"])    

    # Drop rows with missing review text
    combined = combined[combined["review"].str.strip() != ""]

    # Normalize dates
    combined["date"] = combined["date"].apply(normalize_date)

    # Report missing data percentage
    total = len(combined)
    missing = combined["date"].isna().sum() + combined["rating"].isna().sum()
    missing_pct = (missing / (total * 2)) * 100 if total > 0 else 0
    print(f"Rows after dedupe & drop: {total}")
    print(f"Approx missing (%) across date+rating fields: {missing_pct:.2f}%")

    combined.to_csv(OUT_FILE, index=False)
    print(f"Saved cleaned reviews to {OUT_FILE}")


if __name__ == "__main__":
    run()
