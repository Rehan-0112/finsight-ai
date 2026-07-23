"""
rag_chain.py

Connects:
Fusion JSON
→ Query Mapping
→ Retriever
→ Prompt Builder
→ Groq
"""

import json

from src.rag.query_expander import expand_query
from src.rag.retriever import retrieve_multiple
from src.rag.prompts import build_financial_prompt
from src.rag.groq_client import generate_response
from pathlib import Path
from src.evaluation.evaluator import build_report
from src.evaluation.logger import save_report
from src.rag.cache import (
    cache_exists,
    load_cache,
    save_cache
)
from src.config import TOP_K_PER_QUERY

from src.utils.logger import get_logger

logger = get_logger(__name__)

from src.evaluation.report_metrics import average_similarity

logger.info(
    f"Average similarity: {average_similarity(results):.3f}"
)


def load_fusion_payload(ticker: str) -> dict:
    """
    Load the ML fusion output for a ticker.
    """

    fusion_path = Path("data") / "fusion" / f"{ticker}_fusion.json"

    try:
        with open(fusion_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        logger.error(f"Fusion file not found: {fusion_path}")
        raise

    except json.JSONDecodeError:
        logger.error(f"Fusion file is corrupted: {fusion_path}")
        raise


def analyze_ticker(ticker: str):

    logger.info(f"Starting analysis for ticker: {ticker}")

    # -----------------------------
    # Load Fusion JSON
    # -----------------------------

    logger.info("Loading fusion data")

    fusion = load_fusion_payload(ticker)

    search_terms = fusion["explanation"]["rag_search_terms"]

    logger.info("Fusion data loaded successfully")

    # -----------------------------
    # Expand Features into Queries
    # -----------------------------

    logger.info("Generating search queries")

    queries = []

    for feature in search_terms:

        expanded = expand_query(feature)

        for query in expanded:

            queries.append({

                "feature": feature,

                "query": query

            })

    logger.info(f"Generated {len(queries)} search queries")

    # -----------------------------
    # Retrieve Papers
    # -----------------------------

    if cache_exists(ticker):

        logger.info(f"Loading cached retrieval results for {ticker}")

        results = load_cache(ticker)

    else:
        logger.info("Starting retrieval pipeline")

        results = retrieve_multiple(
            queries,
            per_query=TOP_K_PER_QUERY
        )

        logger.info(f"Retrieved {len(results)} final papers")

        try:
            save_cache(
                ticker,
                results
            )

        except Exception:
            logger.exception("Failed to save cache")

    papers = []

    for result in results:

        papers.append({

            "title": result["metadata"]["title"],

            "abstract": result["text"],

            "url": result["metadata"]["pdf_url"],

            "published": result["metadata"].get("published", "Unknown"),

            "feature": result.get("feature", "Unknown"),

            "query": result.get("query", "Unknown"),

            "distance": result["distance"],

            "score": result.get("score", 0),

            "cross_score": result.get("cross_score", 0)

        })

    report = build_report(

        ticker,

        queries,

        papers

    )

    logger.info("Saving evaluation report")

    try:
        save_report(
            ticker,
            report
        )

    except Exception:
        logger.exception("Failed to save evaluation report")

    logger.info("Evaluation report saved")

    # -----------------------------
    # Build Prompt
    # -----------------------------

    logger.info("Building LLM prompt")

    prompt = build_financial_prompt(
        fusion,
        papers
            )

    # -----------------------------
    # Generate Explanation
    # -----------------------------

    logger.info("Sending request to Groq")

    try:
        explanation = generate_response(prompt)

    except Exception as e:
        logger.exception("Groq request failed")
        raise

    logger.info("Groq response received")

    logger.info("Groq explanation generated successfully")

    logger.info(f"Analysis completed for {ticker}")

    return {

        "ticker": ticker,

        "forecast": fusion["forecast"],

        "anomaly": fusion["anomaly"],

        "papers_used": papers,

        "llm_explanation": explanation

    }



if __name__ == "__main__":

    result = analyze_ticker("AAPL")

    print(result["llm_explanation"])