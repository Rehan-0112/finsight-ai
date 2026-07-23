"""
cross_encoder_ranker.py

Uses a CrossEncoder to rerank retrieved papers.
"""

from sentence_transformers import CrossEncoder

model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

def rerank(query: str, papers: list):

    pairs = []

    for paper in papers:

        text = (
            paper["metadata"]["title"]
            + " "
            + paper["text"][:1000]
        )

        pairs.append((query, text))

    scores = model.predict(pairs)

    for paper, score in zip(papers, scores):

        paper["cross_score"] = float(score)

    papers.sort(

        key=lambda x: x["cross_score"],

        reverse=True

    )

    return papers