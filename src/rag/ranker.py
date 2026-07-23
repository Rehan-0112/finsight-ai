"""
ranker.py

Ranks retrieved research papers using
multiple quality signals.
"""

from datetime import datetime
from src.rag.financial_filter import financial_score
from src.rag.domain_filter import domain_penalty
from src.rag.feature_score import feature_score
from src.config import (
    SIMILARITY_WEIGHT,
    FINANCE_WEIGHT,
    TITLE_MATCH_WEIGHT,
    KEYWORD_MATCH_WEIGHT,
    RECENT_YEAR,
    MODERN_YEAR,
    OLDER_YEAR,
    RECENT_BONUS,
    MODERN_BONUS,
    OLDER_BONUS,
)



def score_paper(paper: dict, query: str) -> float:
    """
    Higher score = better paper.
    """

    metadata = paper["metadata"]

    score = 0.0

    # ---------------------------------
    # 1. Vector Similarity
    # ---------------------------------

    similarity = 1 - paper["distance"]

    score += similarity * SIMILARITY_WEIGHT

    # ---------------------------------
    # 2. Publication Recency
    # ---------------------------------

    year = 0

    published = metadata.get("published", "")

    try:
        year = datetime.fromisoformat(
            published.replace("Z", "")
        ).year
    except Exception:
        pass

    if year >= RECENT_YEAR:
        score += RECENT_BONUS
    elif year >= MODERN_YEAR:
        score += MODERN_BONUS
    elif year >= OLDER_YEAR:
        score += OLDER_BONUS

    # ---------------------------------
    # 3. Financial keyword score
    # ---------------------------------

    finance = financial_score(paper)

    score += finance * FINANCE_WEIGHT

    # ---------------------------------
    # 4. Feature keyword score
    # ---------------------------------

    score += feature_score(

        paper["feature"],

        paper

    )

    # ---------------------------------
    # 5. Domain Penalty 
    # ---------------------------------

    text = (
        metadata.get("title", "")
        + " "
        + paper["text"]
    ).lower()

    score -= domain_penalty(text)

    # ---------------------------------
    # 6. Title Match
    # ---------------------------------

    title = metadata.get("title", "").lower()

    query_words = query.lower().split()

    title_matches = sum(
        1 for word in query_words
        if word in title
    )

    score += title_matches * TITLE_MATCH_WEIGHT

    # ---------------------------------
    # 7. Keyword Match
    # ---------------------------------

    for word in query.lower().split():

        if word in text:
            score += KEYWORD_MATCH_WEIGHT
    return score