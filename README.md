# FinSight AI

**AI-Powered Financial Intelligence Platform**

FinSight AI is a full-stack financial analytics platform that combines traditional Machine Learning with a Retrieval-Augmented Generation (RAG) pipeline to deliver explainable, research-backed financial insights. Unlike conventional stock prediction tools that just output a number, FinSight AI explains *why* a prediction was made — grounding every insight in academic research from arXiv.

🔗 **Live Demo:** [finsight-ai-financial-advisor.streamlit.app](https://finsight-ai-financial-advisor.streamlit.app)

---

## What Makes This Different

Most financial ML projects stop at "here's the predicted price." FinSight AI goes further:

- The ML model predicts price direction and explains which features drove it using SHAP
- The RAG pipeline retrieves relevant arXiv research papers based on those exact SHAP features
- A Groq-powered LLM synthesises a cited financial analysis combining both the model output and the research
- An AI chat interface lets users ask questions about any ticker with full analysis context

---

## Features

### ML Pipeline
- **XGBoost Binary Classifier** — predicts 3-day price direction (UP/DOWN) with confidence score
- **41 Engineered Features** — moving averages, RSI, volatility, volume ratios, fundamentals, financial health score
- **TimeSeriesSplit Cross-Validation** — 5-fold CV that respects temporal ordering (no data leakage)
- **SHAP Explainability** — TreeExplainer identifies the top features driving each prediction with human-readable interpretations
- **Isolation Forest Anomaly Detection** — flags unusual financial behaviour with z-score breakdowns per feature
- **Fusion Layer** — unifies ML outputs into a structured payload consumed by the RAG chain

### RAG Pipeline
- **arXiv Ingestion** — 200 research papers across q-fin, cs.LG, cs.AI categories
- **Intelligent Query Expansion** — converts SHAP feature names into multiple semantic search queries
- **ChromaDB Vector Store** — sentence-transformers (all-MiniLM-L6-v2) embeddings for semantic retrieval
- **Hybrid Ranking** — combines ChromaDB similarity, financial relevance scoring, and feature-aware scoring
- **Cross-Encoder Reranking** — transformer-based reranker ensures the most relevant papers reach the LLM
- **Groq LLM Integration** — generates cited financial explanations grounded in retrieved research
- **Retrieval Caching** — per-ticker cache prevents repeated ChromaDB queries

### Dashboard
- **Company header** — live price, 1-day return, forecast pill, anomaly status, model accuracy
- **5 Metric cards** — price, profit margin, operating margin, ROE, financial health — each with 30-day SVG sparklines
- **Price chart** — 120-day history with MA30 and MA90 overlays
- **SHAP factors panel** — colour-coded feature importance bars showing what's driving the prediction
- **Technical indicators** — RSI chart with overbought/oversold zones, volume chart
- **Anomaly detection panel** — z-scores per feature with colour-coded severity
- **Financial health gauge** — Plotly gauge from composite health score
- **Competitor benchmarking** — side-by-side fundamentals and forecast directions for all 5 tickers
- **LLM research analysis** — full RAG-generated cited analysis
- **Supporting papers** — clickable arXiv links with feature attribution
- **AI Chat tab** — conversational interface powered by Groq with full analysis context per ticker

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML Forecasting | XGBoost, scikit-learn (TimeSeriesSplit) |
| Explainability | SHAP (TreeExplainer) |
| Anomaly Detection | Isolation Forest |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Store | ChromaDB |
| RAG Orchestration | LangChain |
| Reranking | Cross-Encoder (ms-marco-MiniLM-L-6-v2) |
| LLM | Groq API (openai/gpt-oss-20b) |
| Data | Yahoo Finance API, arXiv API |
| Dashboard | Streamlit, Plotly |
| Language | Python |

---

## Project Structure

```
finsight-ai/
│
├── app/
│   └── dashboard.py          ← Streamlit dashboard
│
├── src/
│   ├── ml/
│   │   ├── feature_engineer.py   ← 41 feature engineering
│   │   ├── forecaster.py         ← XGBoost classifier + CV
│   │   ├── explainer.py          ← SHAP TreeExplainer
│   │   ├── anomaly_detector.py   ← Isolation Forest
│   │   └── fusion.py             ← ML → RAG payload builder
│   │
│   ├── rag/
│   │   ├── chunker.py            ← arXiv JSON chunking
│   │   ├── embedder.py           ← sentence-transformers + ChromaDB
│   │   ├── retriever.py          ← multi-query hybrid retrieval
│   │   ├── query_mapper.py       ← feature → search query mapping
│   │   ├── query_expander.py     ← semantic query expansion
│   │   ├── ranker.py             ← hybrid ranking
│   │   ├── cross_encoder.py      ← reranking
│   │   ├── rag_chain.py          ← full RAG orchestration
│   │   ├── groq_client.py        ← LLM API wrapper
│   │   ├── prompts.py            ← prompt templates
│   │   └── cache.py              ← retrieval caching
│   │
│   ├── data_ingestion/
│   │   ├── fetch_finance.py      ← Yahoo Finance pipeline
│   │   └── fetch_arxiv.py        ← arXiv paper pipeline
│   │
│   └── config.py                 ← centralised configuration
│
├── data/
│   ├── raw/                  ← CSVs + arXiv JSONs
│   ├── processed/            ← engineered features
│   ├── models/               ← trained XGBoost models
│   ├── shap/                 ← SHAP output JSONs
│   ├── fusion/               ← fusion payloads
│   ├── anomalies/            ← anomaly detection results
│   └── vector_store/         ← ChromaDB persistent storage
│
├── requirements.txt
└── README.md
```

---

## Tickers Covered

| Ticker | Company | Exchange |
|---|---|---|
| AAPL | Apple Inc. | NASDAQ |
| MSFT | Microsoft Corp. | NASDAQ |
| INFY | Infosys Ltd. | NYSE |
| TCS.NS | Tata Consultancy Services | BSE |
| TSLA | Tesla Inc. | NASDAQ |

---

## How to Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/Rehan-0112/finsight-ai.git
cd finsight-ai
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the root:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

**5. Run the ML pipeline**
```bash
python -m src.ml.feature_engineer
python -m src.ml.forecaster
python -m src.ml.explainer
python -m src.ml.anomaly_detector
python -m src.ml.fusion
```

**6. Embed arXiv papers into ChromaDB**
```bash
python -m src.rag.chunker
python -m src.rag.embedder
```

**7. Launch the dashboard**
```bash
streamlit run app/dashboard.py
```

---

## Team

Built as a two-person portfolio project targeting data science internships.

| Role | Responsibilities |
|---|---|
| ML Engineer | Feature engineering, XGBoost forecasting, SHAP explainability, Isolation Forest anomaly detection, fusion layer, Streamlit dashboard |
| RAG Engineer | arXiv ingestion, ChromaDB setup, query expansion, hybrid ranking, cross-encoder reranking, Groq LLM integration, RAG chain orchestration |

---

## Disclaimer

This platform is built for educational and portfolio purposes only. Nothing in FinSight AI constitutes financial advice. All predictions are probabilistic model outputs based on historical data and should not be used as the basis for investment decisions.