"""
Tests for cache.py
"""

from src.rag.cache import (
    save_cache,
    load_cache,
    cache_exists
)


def test_cache_roundtrip():

    ticker = "TEST"

    papers = [

        {
            "title": "Paper A",
            "score": 0.9
        }

    ]

    save_cache(
        ticker,
        papers
    )

    assert cache_exists(ticker)

    loaded = load_cache(ticker)

    assert loaded == papers