import os
from pathlib import Path
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Float,
)


def get_database_url():
    return os.environ.get('DATABASE_URL', 'sqlite:///data/bank_reviews.db')


def main():
    db_url = get_database_url()
    print('Using DATABASE_URL=', db_url)
    engine = create_engine(db_url)
    metadata = MetaData()

    banks = Table(
        'banks',
        metadata,
        Column('bank_id', Integer, primary_key=True, autoincrement=True),
        Column('bank_name', String, nullable=False, unique=True),
        Column('app_name', String, nullable=True),
    )

    reviews = Table(
        'reviews',
        metadata,
        Column('review_id', Integer, primary_key=True, autoincrement=True),
        Column('bank_id', Integer, ForeignKey('banks.bank_id', ondelete='CASCADE')),
        Column('review_text', Text),
        Column('rating', Integer),
        Column('review_date', DateTime),
        Column('sentiment_label', String),
        Column('sentiment_score', Float),
        Column('source', String),
        Column('raw_review_id', String),
    )

    # create tables
    print('Creating tables...')
    metadata.create_all(engine)
    print('Tables created (if not existing).')

    # seed banks from processed CSV if available
    candidates = [Path('../data/processed/reviews_thematic.csv'), Path('../data/processed/reviews_clean.csv')]
    df_path = None
    for p in candidates:
        if p.exists():
            df_path = p
            break

    if df_path is None:
        print('No processed CSV found to seed banks. Skipping seeding.')
        return

    try:
        import pandas as pd
    except Exception:
        print('pandas not available; cannot seed banks. Install pandas to seed from CSV.')
        return

    df = pd.read_csv(df_path)
    banks_list = df['bank'].dropna().unique().tolist()
    print('Seeding banks:', banks_list)

    from sqlalchemy import text
    with engine.begin() as conn:
        for b in banks_list:
            # Use dialect-appropriate INSERT to avoid errors
            if engine.dialect.name == 'sqlite':
                conn.execute(text("INSERT OR IGNORE INTO banks (bank_name, app_name) VALUES (:bn, NULL)"), {'bn': b})
            else:
                conn.execute(text("INSERT INTO banks (bank_name, app_name) VALUES (:bn, NULL) ON CONFLICT (bank_name) DO NOTHING"), {'bn': b})

    print('Seeding complete.')


if __name__ == '__main__':
    main()
