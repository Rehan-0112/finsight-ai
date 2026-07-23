"""
Tests for ranker.py
"""

from src.rag.ranker import score_paper


def test_score_returns_float():

    paper = {
        "text": "RSI and moving average forecasting.",

        "metadata": {
            "title": "Technical Analysis",
            "published": "2024"
        },

        "distance": 0.20,

        "feature": "RSI"
    }

    score = score_paper(
        paper,
        "RSI trading strategy"
    )

    assert isinstance(score, float)