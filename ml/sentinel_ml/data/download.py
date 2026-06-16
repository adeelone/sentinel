from __future__ import annotations

import os
from pathlib import Path

from sentinel_ml.data.synthetic import SyntheticConfig, generate_rows, write_csv


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    synthetic_path = root / "data" / "processed" / "synthetic_creditcard.csv"
    write_csv(synthetic_path, generate_rows(SyntheticConfig(rows=5000)))

    if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"):
        print("Kaggle credentials detected. Run:")
        print("kaggle datasets download -d mlg-ulb/creditcardfraud -p data/raw --unzip")
    else:
        print("No Kaggle credentials found. Synthetic demo data written.")
        print("Manual Kaggle path: data/raw/creditcard.csv")
    print(synthetic_path)


if __name__ == "__main__":
    main()

