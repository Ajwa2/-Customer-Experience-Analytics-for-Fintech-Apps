"""Sentiment and Thematic Analysis pipeline.

Usage:
  python scripts/sentiment_thematic.py --model vader
  python scripts/sentiment_thematic.py --model distilbert   # optional if transformers available

Outputs:
  data/processed/reviews_thematic.csv

Notes:
 - By default this uses VADER (fast, no heavy models). If `transformers` is installed and you pass
   `--model distilbert`, it will try to use `distilbert-base-uncased-finetuned-sst-2-english`.
 - Thematic extraction uses TF-IDF to surface candidate keywords and then applies a simple
   rule-based mapping into 3-5 themes per bank.
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict, Counter
import re


THEME_KEYWORDS = {
    "Account Access Issues": ["login", "password", "otp", "pin", "authenticate", "authentication", "access", "blocked"],
    "Transaction Performance": ["slow", "timeout", "failed", "transfer", "transaction", "processing", "declined", "charge"],
    "User Interface & Experience": ["ui", "interface", "app", "layout", "design", "ux", "crash", "freeze", "bug"],
    "Customer Support": ["support", "customer service", "help", "agent", "call", "response", "support team"],
    "Feature Requests": ["feature", "request", "notification", "balance", "report", "integration"]
}


def compute_vader(df, review_col='review'):
    analyzer = SentimentIntensityAnalyzer()
    vader_scores = df[review_col].astype(str).apply(lambda t: analyzer.polarity_scores(t)['compound'])
    labels = vader_scores.apply(lambda s: 'pos' if s >= 0.05 else ('neg' if s <= -0.05 else 'neu'))
    return vader_scores, labels


def compute_distilbert(df, review_col='review'):
    try:
        from transformers import pipeline
    except Exception as e:
        raise RuntimeError('transformers not available: ' + str(e))
    nlp = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
    scores = []
    labels = []
    for t in df[review_col].astype(str):
        out = nlp(t[:512])[0]
        lbl = 'pos' if out['label'].upper().startswith('POS') else 'neg'
        labels.append(lbl)
        s = out['score'] if lbl == 'pos' else -out['score']
        scores.append(s)
    return pd.Series(scores), pd.Series(labels)


def extract_tfidf_keywords(texts, ngram_range=(1,2), top_k=30):
    vect = TfidfVectorizer(ngram_range=ngram_range, max_features=5000, stop_words='english')
    X = vect.fit_transform(texts)
    features = np.array(vect.get_feature_names_out())
    scores = np.asarray(X.sum(axis=0)).ravel()
    top_idx = np.argsort(scores)[::-1][:top_k]
    return features[top_idx].tolist()


def map_keywords_to_themes(keywords):
    theme_map = defaultdict(list)
    for kw in keywords:
        k = kw.lower()
        for theme, words in THEME_KEYWORDS.items():
            for w in words:
                if w in k:
                    theme_map[theme].append(kw)
                    break
    matched = set([kw for kws in theme_map.values() for kw in kws])
    others = [kw for kw in keywords if kw not in matched]
    if others:
        theme_map['Other'] = others
    return dict(theme_map)


def assign_themes_to_review(text, theme_map):
    text_l = text.lower()
    assigned = []
    for theme, kws in theme_map.items():
        for kw in kws:
            if kw.lower() in text_l:
                assigned.append(theme)
                break
    return assigned


def run(input_path, out_path, model='vader'):
    p = Path(input_path)
    if not p.exists():
        print('Input file not found:', p)
        return
    df = pd.read_csv(p)
    if 'review' not in df.columns:
        print('No `review` column found in input')
        return

    if model == 'vader':
        scores, labels = compute_vader(df)
    elif model == 'distilbert':
        try:
            scores, labels = compute_distilbert(df)
        except Exception as e:
            print('Failed to run DistilBERT; falling back to VADER:', e)
            scores, labels = compute_vader(df)
    else:
        raise ValueError('Unknown model: ' + model)

    df['sentiment_score'] = scores
    df['sentiment_label'] = labels

    out_rows = []
    for bank in sorted(df['bank'].unique()):
        bank_df = df[df['bank'] == bank]
        texts = bank_df['review'].astype(str).tolist()
        keywords = extract_tfidf_keywords(texts, ngram_range=(1,2), top_k=50)
        theme_map = map_keywords_to_themes(keywords)
        theme_counts = [(t, len(kws)) for t, kws in theme_map.items()]
        theme_counts = sorted(theme_counts, key=lambda x: x[1], reverse=True)
        chosen_themes = [t for t, _ in theme_counts[:5]]
        for idx, row in bank_df.iterrows():
            assigned = assign_themes_to_review(str(row['review']), theme_map)
            if not assigned and chosen_themes:
                assigned = [chosen_themes[0]]
            out_rows.append({
                'review_id': idx,
                'review_text': row['review'],
                'bank': bank,
                'rating': row.get('rating', None),
                'sentiment_label': row.get('sentiment_label'),
                'sentiment_score': row.get('sentiment_score'),
                'identified_themes': ';'.join(assigned)
            })

    out_df = pd.DataFrame(out_rows)
    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_p, index=False)
    print('Saved thematic analysis to', out_p)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/processed/reviews_clean.csv')
    parser.add_argument('--output', default='data/processed/reviews_thematic.csv')
    parser.add_argument('--model', default='vader', choices=['vader', 'distilbert'])
    args = parser.parse_args()
    run(args.input, args.output, model=args.model)


if __name__ == '__main__':
    cli()
