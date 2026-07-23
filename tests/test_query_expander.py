"""
Tests for query_expander.py
"""

from src.rag.query_expander import expand_query


def test_expand_rsi():

    queries = expand_query("RSI")

    assert isinstance(queries, list)

    assert len(queries) > 0


def test_expand_macd():

    queries = expand_query("MACD")

    assert isinstance(queries, list)

    assert len(queries) > 0


def test_unknown_feature():

    queries = expand_query("UNKNOWN_FEATURE")

    assert isinstance(queries, list)

    assert len(queries) == 1