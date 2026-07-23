from datetime import datetime


def build_report(
    ticker: str,
    queries: list,
    papers: list
) -> dict:

    report = {

        "ticker": ticker,

        "timestamp": datetime.now().isoformat(),

        "total_queries": len(queries),

        "total_papers": len(papers),

        "queries": queries,

        "papers": []

    }

    for paper in papers:

        report["papers"].append({

            "title": paper["title"],

            "published": paper.get("published", "Unknown"),

            "feature": paper.get("feature", "Unknown"),

            "query": paper.get("query", "Unknown"),

            "distance": paper.get("distance", 0),

            "score": paper.get("score", 0),

            "cross_score": paper.get("cross_score", 0),

            "url": paper["url"]

        })

    return report