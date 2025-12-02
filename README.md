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

## Task 3 — Store cleaned data in PostgreSQL

This project includes helper files to create a PostgreSQL schema and insert cleaned reviews into a `bank_reviews` database.

Files added for Task 3:
- `sql/schema.sql`: SQL DDL to create `banks` and `reviews` tables.
- `scripts/db_init.py`: runs `sql/schema.sql` and seeds the `banks` table from `data/processed/reviews_thematic.csv` (falls back to `reviews_clean.csv`).
- `scripts/insert_reviews_to_postgres.py`: reads processed CSV and inserts rows into `reviews` in batches.
- `requirements-db.txt`: helper requirements for DB work (`sqlalchemy`, `psycopg2-binary`).

Quick start (Windows PowerShell):

```powershell
# 1) Install PostgreSQL (see https://www.postgresql.org/download/)
# 2) Create a database and user, e.g. using psql:
#    psql -U postgres -c "CREATE DATABASE bank_reviews;"
#    psql -U postgres -c "CREATE USER reviews_user WITH PASSWORD 'strongpassword';"
#    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE bank_reviews TO reviews_user;"

# 3) Set the connection string (PowerShell):
$env:DATABASE_URL = 'postgresql://reviews_user:strongpassword@localhost:5432/bank_reviews'

# 4) Install DB requirements into your virtualenv:
pip install -r requirements-db.txt

# 5) Initialize schema and seed banks (reads bank names from processed CSV):
python scripts/db_init.py

# 6) Insert reviews (example):
python scripts/insert_reviews_to_postgres.py --source data/processed/reviews_thematic.csv
```




