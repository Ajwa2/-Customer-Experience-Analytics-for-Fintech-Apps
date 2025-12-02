"""Generate and save EDA plots into notebooks/outputs/."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from nltk.corpus import stopwords


def main():
    DATA_PATH = Path("data/processed/reviews_clean.csv")
    out = Path("notebooks/outputs")
    out.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        print("Cleaned data not found at", DATA_PATH)
        return
    df = pd.read_csv(DATA_PATH)
    stop = set(stopwords.words('english'))
    regex = re.compile(r"[^a-zA-Z\s]")

    # Ratings distribution
    plt.figure(figsize=(6,4))
    sns.countplot(x='rating', data=df, palette='viridis')
    plt.title('Ratings distribution (all banks)')
    plt.tight_layout()
    plt.savefig(out / 'ratings_distribution.png', dpi=150)
    plt.close()

    # Sentiment heatmap by bank (ensure sentiment_label exists)
    if 'sentiment_label' not in df.columns:
        print('Warning: sentiment_label column missing; computing with vaderSentiment is recommended in notebook.')
    else:
        ct = pd.crosstab(df['bank'], df['sentiment_label'], normalize='index')
        plt.figure(figsize=(6,3))
        sns.heatmap(ct, annot=True, cmap='vlag')
        plt.title('Sentiment distribution by bank')
        plt.tight_layout()
        plt.savefig(out / 'sentiment_by_bank.png', dpi=150)
        plt.close()

    # Top negative words per bank
    for bank in sorted(df['bank'].unique()):
        if 'sentiment_label' in df.columns:
            neg = df[(df['bank']==bank) & (df['sentiment_label']=='neg')]['review'].astype(str)
        else:
            neg = df[df['bank']==bank]['review'].astype(str)
        words = Counter()
        for text in neg:
            text = regex.sub(' ', text).lower()
            for w in text.split():
                if len(w) > 2 and w not in stop:
                    words[w] += 1
        top = words.most_common(15)
        if not top:
            continue
        words_, counts = zip(*top)
        plt.figure(figsize=(8,4))
        sns.barplot(x=list(counts), y=list(words_), palette='magma')
        plt.title(f'Top negative words for {bank}')
        plt.tight_layout()
        plt.savefig(out / f'top_negative_words_{bank}.png', dpi=150)
        plt.close()

    print('Saved EDA outputs to', out)


if __name__ == '__main__':
    main()
