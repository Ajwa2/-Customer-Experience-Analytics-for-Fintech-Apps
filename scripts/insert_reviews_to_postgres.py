"""Insert processed reviews into PostgreSQL `reviews` table.

Usage:
  - Ensure `DATABASE_URL` env var is set (see scripts/db_init.py for example).
  - Run: `python scripts/insert_reviews_to_postgres.py --source data/processed/reviews_thematic.csv`

The script maps bank names to `banks.bank_id` and inserts rows in batches.
"""
import os
import argparse
from pathlib import Path
from sqlalchemy import create_engine, text
import pandas as pd


def get_database_url():
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise RuntimeError('DATABASE_URL not set. Example: postgresql://user:pass@localhost:5432/bank_reviews')
    return url


def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i+size]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default='data/processed/reviews_thematic.csv')
    parser.add_argument('--batch-size', type=int, default=200)
    args = parser.parse_args()

    src = Path(args.source)
    if not src.exists():
        raise FileNotFoundError(f'Source file not found: {src}')

    df = pd.read_csv(src)
    print('Loaded', src, '->', df.shape)

    db_url = get_database_url()
    engine = create_engine(db_url)

    # load bank mapping
    with engine.connect() as conn:
        res = conn.execute(text('SELECT bank_id, bank_name FROM banks'))
        mapping = {row['bank_name']: row['bank_id'] for row in res}

    # if some banks missing, insert them
    bank_names = df['bank'].dropna().unique().tolist()
    with engine.begin() as conn:
        for b in bank_names:
            if b not in mapping:
                r = conn.execute(text('INSERT INTO banks (bank_name, app_name) VALUES (:b, NULL) RETURNING bank_id'), {'b': b})
                mapping[b] = r.fetchone()['bank_id']

    print('Bank mapping:', mapping)

    # prepare rows
    rows = []
    for _, r in df.iterrows():
        bank = r.get('bank')
        bank_id = mapping.get(bank)
        if not bank_id:
            continue
        review_text = r.get('review_text') or r.get('review') or ''
        rating = int(r.get('rating')) if pd.notna(r.get('rating')) else None
        review_date = r.get('date') or r.get('review_date')
        sentiment_label = r.get('sentiment_label')
        sentiment_score = r.get('sentiment_score') if 'sentiment_score' in r else (r.get('vader') if 'vader' in r else None)
        source = r.get('source') if 'source' in r else 'google_play'
        raw_review_id = r.get('reviewId') if 'reviewId' in r else None
        rows.append((bank_id, review_text, rating, review_date, sentiment_label, sentiment_score, source, raw_review_id))

    total = len(rows)
    print(f'Prepared {total} rows to insert')

    inserted = 0
    insert_sql = text('''
        INSERT INTO reviews (bank_id, review_text, rating, review_date, sentiment_label, sentiment_score, source, raw_review_id)
        VALUES (:bank_id, :review_text, :rating, :review_date, :sentiment_label, :sentiment_score, :source, :raw_review_id)
    ''')

    with engine.begin() as conn:
        for batch in chunked(rows, args.batch_size):
            params = [
                {
                    'bank_id': b,
                    'review_text': rt,
                    'rating': rating,
                    'review_date': review_date,
                    'sentiment_label': sentiment_label,
                    'sentiment_score': sentiment_score,
                    'source': source,
                    'raw_review_id': raw_review_id,
                }
                for (b, rt, rating, review_date, sentiment_label, sentiment_score, source, raw_review_id) in batch
            ]
            conn.execute(insert_sql, params)
            inserted += len(batch)

    print(f'Inserted {inserted} rows into reviews table')


if __name__ == '__main__':
    main()
