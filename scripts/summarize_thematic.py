"""Summarize the thematic analysis results and print KPIs and examples."""
import pandas as pd
from pathlib import Path


def main(path='data/processed/reviews_thematic.csv'):
    p = Path(path)
    if not p.exists():
        print('File not found:', p)
        return
    df = pd.read_csv(p)
    total = len(df)
    print('Total reviews analyzed:', total)
    sent_cov = df['sentiment_label'].notna().sum()
    print(f'Sentiment coverage: {sent_cov} / {total} ({sent_cov/total*100:.1f}%)')
    print('\nPer-bank counts:')
    print(df['bank'].value_counts())

    print('\nThemes summary per bank:')
    for bank in sorted(df['bank'].unique()):
        sub = df[df['bank'] == bank]
        themes = sub['identified_themes'].fillna('')
        exploded = []
        for t in themes:
            for x in str(t).split(';'):
                if x.strip():
                    exploded.append(x.strip())
        counts = pd.Series(exploded).value_counts()
        print(f'\nBank: {bank} — total reviews: {len(sub)}')
        if counts.empty:
            print('  No themes identified')
            continue
        print('  Top themes:')
        for t, c in counts.head(5).items():
            print(f'    {t}: {c}')
        # show examples for top theme
        top_theme = counts.index[0]
        ex = sub[sub['identified_themes'].str.contains(top_theme, na=False)]
        print(f"  Examples for top theme '{top_theme}':")
        for _, r in ex[['review_text','rating','sentiment_score']].head(3).iterrows():
            print(f"    - ({r['rating']}) {r['review_text'][:140]} ... [score={r['sentiment_score']}]")


if __name__ == '__main__':
    main()
