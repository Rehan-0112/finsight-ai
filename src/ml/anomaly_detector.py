import pandas as pd
import numpy as np
import json
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

PROCESSED_DIR = "data/processed/"
MODELS_DIR    = "data/models/"
ANOMALY_DIR   = "data/anomalies/"
os.makedirs(ANOMALY_DIR, exist_ok=True)

# Features most useful for detecting unusual financial behaviour
ANOMALY_FEATURES = [
    "Return_1d", "Return_7d", "Volume_Ratio",
    "Volatility_7d", "Volatility_30d", "RSI_14",
    "profit_margins", "operating_margins",
    "revenue_growth", "debt_to_equity",
    "financial_health_score"
]


def train_anomaly_detector(ticker: str, contamination: float = 0.05):
    """
    Train Isolation Forest on historical data for a ticker.
    contamination = expected % of anomalies in the data (5% default)
    """
    df = pd.read_csv(f"{PROCESSED_DIR}{ticker}_features.csv")
    df = df.dropna(subset=ANOMALY_FEATURES)

    X = df[ANOMALY_FEATURES]

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators  = 200,
        contamination = contamination,
        random_state  = 42
    )
    model.fit(X_scaled)

    # Save model and scaler
    joblib.dump(model,  f"{MODELS_DIR}{ticker}_anomaly.joblib")
    joblib.dump(scaler, f"{MODELS_DIR}{ticker}_anomaly_scaler.joblib")

    # Score entire history to find known anomalies
    scores = model.decision_function(X_scaled)  # lower = more anomalous
    labels = model.predict(X_scaled)            # -1 = anomaly, 1 = normal

    df["anomaly_score"] = scores
    df["is_anomaly"]    = (labels == -1).astype(int)

    n_anomalies = df["is_anomaly"].sum()
    print(f"✅ {ticker} — {n_anomalies} anomalies detected "
          f"out of {len(df)} days ({round(n_anomalies/len(df)*100,1)}%)")

    return model, scaler, df


def detect_current_anomaly(ticker: str) -> dict:
    """
    Check if today's data point is anomalous.
    Returns anomaly status, score, and which features are unusual.
    """
    model_path  = f"{MODELS_DIR}{ticker}_anomaly.joblib"
    scaler_path = f"{MODELS_DIR}{ticker}_anomaly_scaler.joblib"

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No anomaly model for {ticker}. Train first.")

    model  = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    df = pd.read_csv(f"{PROCESSED_DIR}{ticker}_features.csv")
    df = df.dropna(subset=ANOMALY_FEATURES)

    # Latest row
    latest    = df.iloc[[-1]]
    X_latest  = latest[ANOMALY_FEATURES]
    X_scaled  = scaler.transform(X_latest)

    score     = model.decision_function(X_scaled)[0]
    label     = model.predict(X_scaled)[0]
    is_anomaly = label == -1

    # Compare each feature to historical mean/std to explain WHY it's anomalous
    historical = df[ANOMALY_FEATURES]
    means      = historical.mean()
    stds       = historical.std()
    current    = latest[ANOMALY_FEATURES].iloc[0]

    deviations = []
    for feat in ANOMALY_FEATURES:
        z_score = (current[feat] - means[feat]) / (stds[feat] + 1e-9)
        if abs(z_score) > 1.5:
            deviations.append({
                "feature"    : feat,
                "current"    : round(float(current[feat]), 4),
                "historical_mean": round(float(means[feat]), 4),
                "z_score"    : round(float(z_score), 2),
                "direction"  : "above normal" if z_score > 0 else "below normal"
            })

    # Sort by most extreme deviation
    deviations = sorted(deviations, key=lambda x: abs(x["z_score"]), reverse=True)

    result = {
        "ticker"      : ticker,
        "is_anomaly"  : bool(is_anomaly),
        "anomaly_score": round(float(score), 4),
        "status"      : "⚠️ ANOMALY DETECTED" if is_anomaly else "✅ Normal",
        "deviations"  : deviations[:5],
        "summary"     : _summarise(ticker, is_anomaly, deviations)
    }

    # Save
    out_path = f"{ANOMALY_DIR}{ticker}_anomaly.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


def _summarise(ticker: str, is_anomaly: bool, deviations: list) -> str:
    if not is_anomaly:
        return f"{ticker} is behaving within normal historical ranges."

    if not deviations:
        return f"{ticker} shows unusual overall pattern despite individual features appearing normal."

    top = deviations[0]
    return (
        f"{ticker} shows anomalous behaviour. "
        f"Most unusual: {top['feature']} is {top['direction']} "
        f"(current: {top['current']}, "
        f"historical avg: {top['historical_mean']}, "
        f"z-score: {top['z_score']})."
    )


def run_all(tickers: list = None):
    if tickers is None:
        tickers = ["AAPL", "MSFT", "INFY", "TCS.NS", "TSLA"]

    print("=== TRAINING ANOMALY DETECTORS ===\n")
    for t in tickers:
        try:
            train_anomaly_detector(t)
        except Exception as e:
            print(f"❌ {t}: {e}")

    print("\n=== CURRENT ANOMALY CHECK ===\n")
    results = []
    for t in tickers:
        try:
            r = detect_current_anomaly(t)
            results.append(r)
            print(f"  {r['status']}  {t}")
            if r["deviations"]:
                for d in r["deviations"][:3]:
                    print(f"    → {d['feature']}: {d['current']} "
                          f"(avg: {d['historical_mean']}, z: {d['z_score']})")
            print(f"    {r['summary']}\n")
        except Exception as e:
            print(f"❌ {t}: {e}")

    return results


if __name__ == "__main__":
    run_all()