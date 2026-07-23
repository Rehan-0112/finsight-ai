"""
domain_filter.py

Applies penalties to papers that belong to
non-financial domains.
"""

UNWANTED_TERMS = {

    "electricity",

    "power grid",

    "load forecasting",

    "energy",

    "wind",

    "solar",

    "renewable",

    "rainfall",

    "weather",

    "temperature",

    "traffic",

    "medical",

    "covid",

    "protein",

    "disease",

    "genome",

    "dna",

    "rna",

    "satellite",

    "remote sensing"

}


def domain_penalty(text: str) -> float:
    """
    Returns a penalty score for papers that are likely
    unrelated to financial forecasting.
    """

    text = text.lower()

    penalty = 0

    for word in UNWANTED_TERMS:

        if word in text:
            penalty += 0.15

    return penalty