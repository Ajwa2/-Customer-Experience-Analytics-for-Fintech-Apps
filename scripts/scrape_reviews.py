"""Scrape Google Play reviews for target bank apps.

Usage:
    python scripts/scrape_reviews.py

This script will:
 - Fetch reviews for the configured apps until the per-app target is met
 - Save raw per-bank CSV files under `data/raw/`

Notes:
 - Requires internet access and the `google_play_scraper` package.
 - Adjust `TARGET_PER_BANK` if you want more/less reviews.
"""
from pathlib import Path
import time
import csv
from datetime import datetime
from google_play_scraper import reviews, Sort


APPS = {
    "CBE": "com.combanketh.mobilebanking",
    "BOA": "com.boa.boaMobileBanking",
    "DASHEN": "com.dashen.dashensuperapp",
}

TARGET_PER_BANK = 400
BATCH_SIZE = 200


def fetch_reviews_for_app(app_id, target=TARGET_PER_BANK, lang="en", country="us"):
    all_reviews = []
    token = None
    while len(all_reviews) < target:
        count = min(BATCH_SIZE, target - len(all_reviews))
        result, token = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=count,
            continuation_token=token,
        )
        if not result:
            break
        all_reviews.extend(result)
        if not token:
            break
        time.sleep(1)
    return all_reviews[:target]


def save_reviews_csv(reviews_list, bank_key, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"raw_{bank_key}.csv"
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["content", "score", "at", "bank", "source"])
        for r in reviews_list:
            content = r.get("content") or ""
            score = r.get("score")
            at = r.get("at")
            at_iso = at.isoformat() if at else ""
            writer.writerow([content, score, at_iso, bank_key, "google_play"])
    return out_path


def main():
    base = Path("data/raw")
    summary = {}
    for bank_key, app_id in APPS.items():
        print(f"Fetching reviews for {bank_key} ({app_id}) ...")
        reviews_list = fetch_reviews_for_app(app_id)
        path = save_reviews_csv(reviews_list, bank_key, base)
        print(f"Saved {len(reviews_list)} reviews to {path}")
        summary[bank_key] = len(reviews_list)

    print("Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
