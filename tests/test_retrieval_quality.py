from src.rag.retriever import retrieve_multiple

def test_rsi_retrieval():

    queries = [
        {
            "feature": "RSI",
            "query": "RSI stock prediction"
        }
    ]

    papers = retrieve_multiple(queries)

    assert len(papers) > 0

    text = " ".join(
        paper["text"].lower()
        for paper in papers
    )

    assert "rsi" in text