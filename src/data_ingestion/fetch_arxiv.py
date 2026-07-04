import arxiv
import json
import os

def fetch_arxiv_papers(query: str, max_results: int = 50) -> list:
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    papers = []
    for result in client.results(search):
        papers.append({
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "abstract": result.summary,
            "published": str(result.published),
            "url": result.entry_id,
            "pdf_url": result.pdf_url,
            "categories": result.categories
        })
    return papers

def save_papers(query: str, filename: str, output_dir: str = "data/raw/"):
    os.makedirs(output_dir, exist_ok=True)
    papers = fetch_arxiv_papers(query)
    output_path = f"{output_dir}{filename}.json"
    with open(output_path, "w") as f:
        json.dump(papers, f, indent=2)
    print(f"✅ Saved {len(papers)} papers → {output_path}")

if __name__ == "__main__":
    queries = {
        "revenue_forecasting": "revenue forecasting financial prediction",
        "anomaly_detection_finance": "anomaly detection financial time series",
        "explainable_ai_finance": "explainable AI financial forecasting SHAP",
        "llm_finance": "large language models financial analysis"
    }
    for filename, query in queries.items():
        save_papers(query, filename)