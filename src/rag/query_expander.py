"""
query_expander.py

Expands a financial feature into multiple
search queries for better retrieval.
"""


from src.rag.query_mapper import feature_to_query


QUERY_EXPANSIONS = {

    "RSI": [
        "relative strength index stock prediction",
        "RSI technical analysis equity markets",
        "momentum indicators stock forecasting",
        "RSI trading strategy research",
        "financial momentum indicators"
    ],

    "MA_90": [
        "moving average stock price prediction",
        "long term moving average trading strategy",
        "technical analysis moving average equity markets",
        "trend following stock forecasting",
        "moving average financial time series"
    ],

    "MA_30": [
        "30 day moving average stock forecasting",
        "medium term moving average trading",
        "technical analysis moving average stocks",
        "financial trend following models",
        "moving average equity prediction"
    ],

    "MA_7": [
        "short term moving average stock prediction",
        "technical analysis short term trends",
        "moving average trading signals",
        "short term equity forecasting",
        "moving average financial forecasting"
    ],

    "Volatility": [
        "stock market volatility forecasting",
        "equity market volatility prediction",
        "financial asset volatility modeling",
        "stock price risk forecasting",
        "volatility forecasting in equity markets"
    ],

    "Volatility_7d": [
        "short term stock market volatility forecasting",
        "financial volatility prediction",
        "equity market volatility models",
        "volatility forecasting stock returns",
        "risk forecasting financial markets"
    ],

    "Volatility_30d": [
        "long term stock volatility forecasting",
        "financial risk prediction",
        "equity volatility models",
        "volatility forecasting finance",
        "asset price volatility prediction"
    ],

    "Return_7d": [
        "stock return prediction",
        "equity return forecasting",
        "financial return prediction models",
        "asset return forecasting",
        "short term stock return analysis"
    ],

    "MACD": [
        "MACD stock trading strategy",
        "moving average convergence divergence research",
        "technical indicators stock prediction",
        "MACD equity forecasting",
        "financial technical analysis MACD"
    ],

}

def expand_query(feature: str) -> list[str]:

    if feature in QUERY_EXPANSIONS:
        return QUERY_EXPANSIONS[feature]

    return [feature_to_query(feature)]