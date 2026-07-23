"""
cache.py

Simple retrieval cache.
"""

import json
from pathlib import Path


CACHE_DIR = Path("data") / "cache"

CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_exists(
    ticker: str
) -> bool:

    return (CACHE_DIR / f"{ticker}.json").exists()


def load_cache(
    ticker: str
) -> list:

    with open(CACHE_DIR / f"{ticker}.json", "r", encoding="utf-8") as f:

        return json.load(f)

def save_cache(
    ticker: str,
    papers: list
) -> None:

    with open(CACHE_DIR / f"{ticker}.json", "w", encoding="utf-8") as f:

        json.dump(papers, f, indent=4)