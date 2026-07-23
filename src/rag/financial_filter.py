from src.rag.keywords import FINANCE_KEYWORDS


def financial_score(paper: dict) -> int:
    """
    Scores how finance-related a paper is.
    """

    text = (
        paper["metadata"]["title"] +
        " " +
        paper["text"]
    ).lower()

    score = 0

    for keyword in FINANCE_KEYWORDS:

        if keyword.lower() in text:
            score += 1

    return score