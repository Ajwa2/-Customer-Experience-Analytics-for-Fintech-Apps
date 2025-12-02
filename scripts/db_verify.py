"""Verify data in the database: prints total reviews and per-bank counts.

Usage:
  $env:DATABASE_URL = 'sqlite:///data/bank_reviews.db'
  python scripts/db_verify.py
"""
import os
from sqlalchemy import create_engine, text


def get_database_url():
    return os.environ.get('DATABASE_URL', 'sqlite:///data/bank_reviews.db')


def main():
    db_url = get_database_url()
    print('Connecting to', db_url)
    engine = create_engine(db_url)
    with engine.connect() as conn:
        try:
            total = conn.execute(text('SELECT COUNT(*) FROM reviews')).scalar()
        except Exception as e:
            print('Error querying reviews table:', e)
            return
        print('Total reviews in DB:', total)

        rows = conn.execute(text('SELECT b.bank_name, COUNT(*) AS cnt FROM banks b JOIN reviews r ON b.bank_id = r.bank_id GROUP BY b.bank_name ORDER BY cnt DESC'))
        print('\nPer-bank counts:')
        for r in rows:
            # result row may be a tuple depending on driver; print by index
            try:
                print(f"- {r['bank_name']}: {r['cnt']}")
            except Exception:
                print(f"- {r[0]}: {r[1]}")


if __name__ == '__main__':
    main()
