FEATURE_TERMS = {

    "RSI": [
        "relative strength index",
        "RSI"
    ],

    "MACD": [
        "moving average convergence divergence",
        "MACD"
    ],

    "MA_7": [
        "moving average",
        "trend following"
    ],

    "MA_30": [
        "moving average",
        "trend following"
    ],

    "MA_90": [
        "moving average",
        "trend following"
    ],

    "Volatility": [
        "volatility",
        "risk"
    ],

    "Volatility_7d": [
        "volatility",
        "risk"
    ],

    "Volatility_30d": [
        "volatility",
        "risk"
    ],

    "Return_7d": [
        "return",
        "returns"
    ]

}

def feature_score(
    feature: str,
    paper: dict
) -> float:

    if feature not in FEATURE_TERMS:
        return 0

    text = (
        paper["metadata"]["title"] +
        " " +
        paper["text"]
    ).lower()

    score = 0

    for term in FEATURE_TERMS[feature]:

        if term.lower() in text:
            score += 0.08

    return score