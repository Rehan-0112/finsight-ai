"""
Evaluate retrieval quality.
"""

from collections import Counter


def summarize_features(papers: list) -> Counter:

    features = [
        paper.get("feature", "Unknown")
        for paper in papers
    ]

    return Counter(features)