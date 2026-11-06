"""
Download the Olist dataset from Kaggle into data/raw/.

Needs a Kaggle API token:
  1. kaggle.com → Settings → API → "Create New Token" (downloads kaggle.json)
  2. Put it at ~/.kaggle/kaggle.json   (Windows: C:\\Users\\<you>\\.kaggle\\kaggle.json)

    pip install kaggle
    python src/download_data.py
"""

from pathlib import Path

DATASET = "olistbr/brazilian-ecommerce"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"


def main() -> None:
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        raise SystemExit("Install the Kaggle client first:  pip install kaggle")

    RAW.mkdir(parents=True, exist_ok=True)
    api = KaggleApi()
    api.authenticate()
    print(f"Downloading {DATASET} → {RAW} ...")
    api.dataset_download_files(DATASET, path=str(RAW), unzip=True)
    for f in sorted(RAW.glob("*.csv")):
        print(f"  {f.name:<45} {f.stat().st_size / 1e6:6.1f} MB")


if __name__ == "__main__":
    main()
