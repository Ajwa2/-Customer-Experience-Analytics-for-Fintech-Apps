"""Initialize PostgreSQL database schema and seed `banks` table.

Usage:
  - Set environment variable `DATABASE_URL`, e.g.
      export DATABASE_URL=postgresql://user:pass@localhost:5432/bank_reviews
    On Windows PowerShell:
      $env:DATABASE_URL = 'postgresql://user:pass@localhost:5432/bank_reviews'

  - Run: `python scripts/db_init.py`

This script executes `sql/schema.sql` and seeds the `banks` table with banks
detected in `data/processed/reviews_thematic.csv` (or `reviews_clean.csv`).
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, text


def get_database_url():
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise RuntimeError('DATABASE_URL not set. Example: postgresql://user:pass@localhost:5432/bank_reviews')
    return url


def main():
    db_url = get_database_url()
    engine = create_engine(db_url)

    # run schema.sql
    schema_path = Path('sql/schema.sql')
    if not schema_path.exists():
        raise FileNotFoundError(f'Missing schema file: {schema_path}')

    print('Applying schema:', schema_path)
    with engine.connect() as conn:
        sql_text = schema_path.read_text(encoding='utf-8')
        conn.execute(text(sql_text))
        conn.commit()

    # attempt to seed banks from processed CSV
    candidates = [Path('data/processed/reviews_thematic.csv'), Path('data/processed/reviews_clean.csv')]
    df_path = None
    for p in candidates:
        if p.exists():
            df_path = p
            break

    if df_path is None:
        print('No processed CSV found to seed banks (expected at data/processed/reviews_thematic.csv or reviews_clean.csv).')
        return

    import pandas as pd
    df = pd.read_csv(df_path)
    banks = df['bank'].dropna().unique().tolist()
    print('Seeding banks:', banks)

    with engine.begin() as conn:
        for b in banks:
            # insert if not exists
            conn.execute(text("""
                INSERT INTO banks (bank_name, app_name)
                VALUES (:bank_name, NULL)
                ON CONFLICT (bank_name) DO NOTHING;
            """), {'bank_name': b})

    print('Database initialized and banks seeded.')


if __name__ == '__main__':
    main()
