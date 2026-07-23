"""
config.py

Central configuration for FinSight AI.
"""

# -----------------------------
# Retrieval
# -----------------------------

VECTOR_DB_PATH = "data/vector_store"
COLLECTION_NAME = "finance_papers"

TOP_K_PER_QUERY = 10
TOP_K_RERANK = 20
FINAL_TOP_K = 5

# -----------------------------
# Ranking Weights
# -----------------------------

SIMILARITY_WEIGHT = 0.60
FINANCE_WEIGHT = 0.03
TITLE_MATCH_WEIGHT = 0.05
KEYWORD_MATCH_WEIGHT = 0.02

# -----------------------------
# Publication Bonuses
# -----------------------------

RECENT_YEAR = 2024
MODERN_YEAR = 2020
OLDER_YEAR = 2015

RECENT_BONUS = 0.20
MODERN_BONUS = 0.15
OLDER_BONUS = 0.10

GROQ_MODEL = "llama-3.3-70b-versatile"