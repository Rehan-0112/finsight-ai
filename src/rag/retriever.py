"""
retriever.py

Retrieves relevant research papers from ChromaDB.
Supports both single-query and multi-query retrieval.
"""

from chromadb import PersistentClient
from src.rag.ranker import score_paper

from src.rag.cross_encoder_ranker import rerank
from src.config import (
    VECTOR_DB_PATH,
    COLLECTION_NAME,
    TOP_K_PER_QUERY,
    TOP_K_RERANK,
    FINAL_TOP_K,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# -------------------------------------
# Connect to ChromaDB
# -------------------------------------

try:
    client = PersistentClient(path=VECTOR_DB_PATH)

    collection = client.get_collection(COLLECTION_NAME)

    logger.info(
        f"Connected to ChromaDB collection: {COLLECTION_NAME}"
    )

except Exception:
    logger.exception(
        "Failed to initialize ChromaDB"
    )
    raise

# -------------------------------------
# Basic Retrieval (V1 Compatibility)
# -------------------------------------

def retrieve_documents(query: str, n_results: int = 5):
    
    logger.info(
        f"Searching ChromaDB for query: {query}"
    )

    try:

        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

    except Exception:
        logger.exception(
            f"ChromaDB query failed for '{query}'"
        )
        raise

    if (
        not results.get("documents")
        or not results["documents"]
        or not results["documents"][0]
    ):
        logger.warning(
            f"No papers found for query: {query}"
        )
        return []

        logger.warning(
            f"No papers found for query: {query}"
        )

        return []

    retrieved = []

    for i in range(len(results["documents"][0])):

        retrieved.append({

            "text": results["documents"][0][i],

            "metadata": results["metadatas"][0][i],

            "distance": results["distances"][0][i]

        })

    logger.info(
        f"Retrieved {len(retrieved)} papers for query: {query}"
    )

    return retrieved


# -------------------------------------
# Smart Multi-Query Retrieval (V2)
# -------------------------------------

def retrieve_multiple(
    queries: list,
    per_query: int = TOP_K_PER_QUERY
):

    logger.info(
        f"Running multi-query retrieval with {len(queries)} queries"
    )

    papers = {}

    for item in queries:

        feature = item["feature"]

        query = item["query"]

        results = retrieve_documents(
            query,
            n_results=per_query
        )

        for paper in results:

            paper_id = paper["metadata"]["pdf_url"]

            # Remember which query retrieved this paper
            paper["query"] = query
            paper["feature"] = feature

            # Keep only the best similarity
            if (
                paper_id not in papers
                or paper["distance"] < papers[paper_id]["distance"]
            ):

                papers[paper_id] = paper

    ranked = []

    for paper in papers.values():

        try:

            score = score_paper(
                paper,
                paper["query"]
            )

        except Exception:

            logger.exception(
                f"Failed to score paper: {paper['metadata'].get('title', 'Unknown')}"
            )

            continue
        paper["score"] = score

        ranked.append(paper)

    ranked.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    if not ranked:

        logger.warning(
            "No papers available after ranking"
        )

        return []

    logger.info(
        f"Ranked {len(ranked)} unique papers"
    )

    combined_query = " ".join(
        item["query"]
        for item in queries
    )

    # Only rerank the best candidates
    top_candidates = ranked[:TOP_K_RERANK]

    logger.info(
        f"Cross-encoder reranking {len(top_candidates)} papers"
    )

    try:

        reranked = rerank(
            combined_query,
            top_candidates
        )

    except Exception:

        logger.exception(
            "Cross-encoder reranking failed"
        )

        raise

    logger.info(
        f"Cross-encoder completed. Returning top {FINAL_TOP_K} papers"
    )

    return reranked[:FINAL_TOP_K]