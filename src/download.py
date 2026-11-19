"""Download the raw flotation plant data into data/raw/.

Usage:  python -m src.download
"""
from src.data import download_raw

if __name__ == "__main__":
    path = download_raw()
    print("Raw data ready:", path)
