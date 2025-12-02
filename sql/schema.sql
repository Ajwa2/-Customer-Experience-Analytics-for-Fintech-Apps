-- Schema for bank_reviews database
-- Run with: psql -d bank_reviews -f sql/schema.sql

CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name TEXT NOT NULL UNIQUE,
    app_name TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER REFERENCES banks(bank_id) ON DELETE CASCADE,
    review_text TEXT,
    rating INTEGER,
    review_date TIMESTAMP WITH TIME ZONE,
    sentiment_label TEXT,
    sentiment_score REAL,
    source TEXT,
    raw_review_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX IF NOT EXISTS idx_reviews_review_date ON reviews(review_date);
