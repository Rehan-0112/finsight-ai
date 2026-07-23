"""
query_generator.py

Uses Groq to generate research search queries.
"""

from src.rag.groq_client import generate_response


def generate_queries(feature: str):

    prompt = f"""
You are a financial research assistant.

Generate exactly 5 different search queries
for academic papers about:

{feature}

Return ONLY the queries.

One query per line.
"""

    response = generate_response(prompt)

    return [
        line.strip("- ").strip()
        for line in response.splitlines()
        if line.strip()
    ]