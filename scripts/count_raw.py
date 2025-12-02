"""Count rows in data/raw/raw_*.csv files (excluding header)."""
from pathlib import Path
import csv


def main():
    p = Path("data/raw")
    if not p.exists():
        print("No data/raw directory found.")
        return
    total = 0
    for f in sorted(p.glob("raw_*.csv")):
        with f.open(encoding="utf-8") as fh:
            reader = csv.reader(fh)
            rows = list(reader)
        count = max(0, len(rows) - 1)
        print(f"{f.name}: {count} rows")
        total += count
    print(f"TOTAL: {total} rows")


if __name__ == "__main__":
    main()
