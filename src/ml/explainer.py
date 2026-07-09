import pandas as pd
import numpy as np
import json
import os
import shap
import joblib
from forecaster import prepare_xy, FEATURE_COLS

PROCESSED_DIR = "data/processed/"
MODELS_DIR    = "data/models/"
SHAP_DIR      = "data/shap/"
os.makedirs(SHAP_DIR, exist_ok=True)


def explain_prediction(ticker: str, horizon: int = 3) -> dict:
    """
    Run SHAP on the latest data point for a ticker.
    Returns top features driving the prediction with their impact values.
    """
    # Load model and data
    model = joblib.load(f"{MODELS_DIR}{ticker}_forecaster.joblib")
    df    = pd.read_csv(f"{PROCESSED_DIR}{ticker}_features.csv")
    X, y, _, _ = prepare_xy(df, horizon=horizon)

    # Use latest row as the current state
    X_latest = X.iloc[[-1]]

    # SHAP explainer — TreeExplainer is fast for XGBoost
    explainer  = shap.TreeExplainer(model)
    shap_vals  = explainer.shap_values(X_latest)

    # For binary classification, shap_values returns list of 2 arrays
    # Index 1 = SHAP values for class 1 (UP)
    if isinstance(shap_vals, list):
        sv = shap_vals[1][0]
    else:
        sv = shap_vals[0]

    # Build feature → shap_value mapping
    shap_dict = dict(zip(FEATURE_COLS, sv))

    # Sort by absolute impact
    sorted_features = sorted(shap_dict.items(),
                             key=lambda x: abs(x[1]),
                             reverse=True)

    # Top 5 contributors
    top_features = [
        {
            "feature"  : feat,
            "shap_value": round(float(val), 6),
            "impact"   : "positive" if val > 0 else "negative",
            "meaning"  : _interpret(feat, val, df)
        }
        for feat, val in sorted_features[:5]
    ]

    # Get prediction info
    direction   = model.predict(X_latest)[0]
    proba       = model.predict_proba(X_latest)[0]
    confidence  = round(float(max(proba)) * 100, 1)

    result = {
        "ticker"        : ticker,
        "direction"     : "UP" if direction == 1 else "DOWN",
        "confidence_pct": confidence,
        "top_features"  : top_features,
        "all_shap"      : {k: round(float(v), 6) for k, v in shap_dict.items()},
        "current_values": X_latest.iloc[0].to_dict()
    }

    # Save for RAG fusion layer
    out_path = f"{SHAP_DIR}{ticker}_shap.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


def _interpret(feature: str, shap_val: float, df: pd.DataFrame) -> str:
    """
    Human-readable interpretation of each feature's SHAP contribution.
    """
    direction = "pushing price UP" if shap_val > 0 else "pushing price DOWN"
    val = df[feature].iloc[-1] if feature in df.columns else None

    interpretations = {
        "RSI_14"              : f"RSI at {round(val,1) if val else 'N/A'} — "
                                f"{'overbought signal' if val and val > 70 else 'oversold signal' if val and val < 30 else 'neutral momentum'} ({direction})",
        "MA_cross"            : f"7-day MA {'above' if val else 'below'} 30-day MA ({direction})",
        "Price_above_MA30"    : f"Price {'above' if val else 'below'} 30-day average ({direction})",
        "Price_above_MA90"    : f"Price {'above' if val else 'below'} 90-day average ({direction})",
        "Volatility_30d"      : f"30-day volatility at {round(val,4) if val else 'N/A'} ({direction})",
        "Return_7d"           : f"7-day return at {round(val*100,2) if val else 'N/A'}% ({direction})",
        "Return_30d"          : f"30-day return at {round(val*100,2) if val else 'N/A'}% ({direction})",
        "Volume_Ratio"        : f"Volume {round(val,2) if val else 'N/A'}x above average ({direction})",
        "financial_health_score": f"Health score {round(val,1) if val else 'N/A'}/100 ({direction})",
        "debt_to_equity"      : f"Debt/Equity ratio at {round(val,2) if val else 'N/A'} ({direction})",
        "profit_margins"      : f"Profit margin at {round(val*100,2) if val else 'N/A'}% ({direction})",
        "revenue_growth"      : f"Revenue growth at {round(val*100,2) if val else 'N/A'}% ({direction})",
        "operating_margins"   : f"Operating margin at {round(val*100,2) if val else 'N/A'}% ({direction})",
        "return_on_equity"    : f"ROE at {round(val*100,2) if val else 'N/A'}% ({direction})",
        "earnings_growth"     : f"Earnings growth at {round(val*100,2) if val else 'N/A'}% ({direction})",
    }

    return interpretations.get(feature, f"{feature} is {direction}")


def explain_all(tickers: list = None, horizon: int = 3):
    if tickers is None:
        tickers = ["AAPL", "MSFT", "INFY", "TCS.NS", "TSLA"]

    print("\n=== SHAP EXPLANATIONS ===\n")
    for ticker in tickers:
        try:
            result = explain_prediction(ticker, horizon=horizon)
            print(f"{'─'*50}")
            print(f"  {ticker}  →  {result['direction']} "
                  f"({result['confidence_pct']}% confidence)")
            print(f"  Top drivers:")
            for f in result["top_features"]:
                sign = "▲" if f["impact"] == "positive" else "▼"
                print(f"    {sign} {f['feature']:<25} SHAP: {f['shap_value']:>8.4f}")
                print(f"      └─ {f['meaning']}")
            print()
        except Exception as e:
            print(f"❌ {ticker}: {e}")

    print(f"\n✅ SHAP JSONs saved to {SHAP_DIR}")


if __name__ == "__main__":
    explain_all()