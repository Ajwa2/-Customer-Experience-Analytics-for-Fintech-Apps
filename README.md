# Customer Experience Analytics for Fintech Apps

This repository provides a starter scaffold for Python projects focused on customer experience analytics for fintech applications.

**Folder structure**

├── .vscode/
│   └── settings.json
├── .github/
│   └── workflows
│       └── unittests.yml
├── .gitignore
├── requirements.txt
├── README.md
├── src/
│   └── __init__.py
├── notebooks/
│   ├── __init__.py
│   └── README.md
├── tests/
│   └── __init__.py
└── scripts/
    ├── __init__.py
    └── README.md
```

## Task 1 — Data collection & preprocessing (Google Play reviews)

This repository includes scripts to scrape and preprocess Google Play reviews for the three target bank apps. The objective for Task 1 is:

- Collect at least **400 reviews per bank** (1,200+ total) from Google Play.
- Keep missing data under **5%** for required fields (`review`, `rating`, `date`).
- Produce a clean CSV `data/processed/reviews_clean.csv` with columns: `review,rating,date,bank,source`.

How to run (PowerShell):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/scrape_reviews.py
python scripts/preprocess_reviews.py
```

Files added for Task 1:

- `scripts/scrape_reviews.py`: fetches reviews using `google_play_scraper` and saves per-bank raw CSVs to `data/raw/`.
- `scripts/preprocess_reviews.py`: cleans, deduplicates, normalizes dates and combines raw CSVs into `data/processed/reviews_clean.csv`.

Notes:
- Network access is required to run the scraper. If you run into Play Store rate limits, consider adding longer sleeps between requests, or using smaller batch sizes.
- The scraping and preprocessing scripts are committed on the `task-1` branch; follow the Git instructions below to work on that branch.


