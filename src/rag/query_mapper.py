"""
query_mapper.py

Converts ML feature names into natural-language search queries
for semantic retrieval from ChromaDB.
"""

FEATURE_QUERY_MAP = {
    "MA_7": "7 day moving average stock price forecasting",
    "MA_30": "30 day moving average financial forecasting",
    "MA_90": "90 day moving average stock forecasting",

    "Return_1d": "daily stock return prediction",
    "Return_7d": "short term stock return forecasting",
    "Return_30d": "monthly stock return prediction",

    "Volatility_7d": "short term stock market volatility forecasting",
    "Volatility_30d": "market volatility impact on stock prediction",

    "Volume_Ratio": "trading volume impact on stock prices",

    "RSI_14": "relative strength index RSI financial forecasting",

    "Price_above_MA30": "moving average crossover stock trend",

    "Price_above_MA90": "long term trend analysis using moving averages",

    "MA_cross": "moving average crossover trading strategy",

    "profit_margins": "profit margin impact on company performance",

    "debt_to_equity": "debt to equity ratio impact on stock valuation",

    "operating_margins": "operating margin financial performance",

    "earnings_growth": "earnings growth prediction",

    "revenue_growth": "revenue growth forecasting",

    "current_ratio": "current ratio financial health",

    "return_on_equity": "return on equity ROE financial analysis",

    "financial_health_score": "financial health score company valuation"
}


def feature_to_query(feature: str) -> str:
    """
    Convert ML feature name into a semantic search query.
    Falls back to the original feature if unknown.
    """

    return FEATURE_QUERY_MAP.get(
        feature_name,
        feature_name.replace("_", " ")
    )