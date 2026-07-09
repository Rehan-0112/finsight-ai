import json
import os
import sys

# Make sure src/ is on the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.forecaster       import predict
from ml.explainer        import explain_prediction
from ml.anomaly_detector import detect_current_anomaly

SHAP_DIR    = "data/shap/"
ANOMALY_DIR = "data/anomalies/"
FUSION_DIR  = "data/fusion/"
os.makedirs(FUSION_DIR, exist_ok=True)


def build_fusion_payload(ticker: str, horizon: int = 3) -> dict:
    """
    Combines ML outputs into a single payload that the RAG chain
    can consume to generate cited, LLM-powered explanations.
    """
    print(f"\n🔗 Building fusion payload for {ticker}...")

    # ── 1. Forecaster output ──────────────────────────────────────────────────
    forecast = predict(ticker, horizon=horizon)

    # ── 2. SHAP explanation ───────────────────────────────────────────────────
    shap_result = explain_prediction(ticker, horizon=horizon)

    # Top SHAP features as plain search queries for ChromaDB
    top_features    = shap_result["top_features"]
    rag_search_terms = [f["feature"] for f in top_features[:3]]

    # ── 3. Anomaly detection ──────────────────────────────────────────────────
    anomaly = detect_current_anomaly(ticker)

    # ── 4. Build unified payload ──────────────────────────────────────────────
    payload = {

        # Identity
        "ticker"  : ticker,
        "horizon" : horizon,

        # Forecast
        "forecast": {
            "direction"     : forecast["direction"],
            "confidence_pct": forecast["confidence_pct"],
            "current_price" : forecast["current_price"],
            "avg_accuracy"  : forecast["avg_accuracy"],
        },

        # SHAP — what drove the prediction
        "explanation": {
            "top_features"   : top_features,
            "all_shap"       : shap_result["all_shap"],
            "rag_search_terms": rag_search_terms,
        },

        # Anomaly status
        "anomaly": {
            "is_anomaly"    : anomaly["is_anomaly"],
            "status"        : anomaly["status"],
            "summary"       : anomaly["summary"],
            "deviations"    : anomaly["deviations"],
        },

        # Pre-built prompt context for the LLM
        "llm_context": _build_llm_context(ticker, forecast,
                                           shap_result, anomaly),
    }

    # Save for RAG chain to pick up
    out_path = f"{FUSION_DIR}{ticker}_fusion.json"
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"  ✅ Fusion payload saved → {out_path}")
    return payload


def _build_llm_context(ticker, forecast, shap_result, anomaly) -> str:
    """
    Formats ML outputs into a structured text context
    that gets injected into the RAG prompt alongside retrieved papers.
    """
    top = shap_result["top_features"]

    feature_lines = "\n".join([
        f"  - {f['feature']}: SHAP={f['shap_value']:.4f} "
        f"({'↑ bullish' if f['impact'] == 'positive' else '↓ bearish'}) "
        f"— {f['meaning']}"
        for f in top
    ])

    anomaly_line = (
        f"⚠️ ANOMALY DETECTED: {anomaly['summary']}"
        if anomaly["is_anomaly"]
        else f"✅ No anomaly detected — {anomaly['summary']}"
    )

    context = f"""
=== ML ANALYSIS FOR {ticker} ===

FORECAST (next {forecast['horizon_days']} days):
  Direction  : {forecast['direction']}
  Confidence : {forecast['confidence_pct']}%
  Current Price: ${forecast['current_price']}
  Model Accuracy: {forecast['avg_accuracy']*100:.1f}%

TOP PREDICTION DRIVERS (SHAP):
{feature_lines}

ANOMALY CHECK:
  {anomaly_line}

RAG SEARCH CONTEXT:
  The following features are driving this prediction and should be
  used to retrieve relevant academic research:
  {', '.join([f['feature'] for f in top[:3]])}
"""
    return context.strip()


def run_all(tickers: list = None, horizon: int = 3):
    if tickers is None:
        tickers = ["AAPL", "MSFT", "INFY", "TCS.NS", "TSLA"]

    print("=" * 55)
    print("  FINSIGHT AI — FUSION LAYER")
    print("=" * 55)

    payloads = []
    for t in tickers:
        try:
            payload = build_fusion_payload(t, horizon=horizon)
            payloads.append(payload)

            print(f"\n  📊 {t} Summary:")
            print(f"     Direction : {payload['forecast']['direction']} "
                  f"({payload['forecast']['confidence_pct']}%)")
            print(f"     Anomaly   : {payload['anomaly']['status']}")
            print(f"     RAG terms : {payload['explanation']['rag_search_terms']}")

        except Exception as e:
            print(f"  ❌ {t}: {e}")

    print(f"\n{'='*55}")
    print(f"  ✅ {len(payloads)} fusion payloads ready for RAG chain")
    print(f"  📁 Saved to {FUSION_DIR}")
    print(f"{'='*55}")

    return payloads


if __name__ == "__main__":
    run_all()