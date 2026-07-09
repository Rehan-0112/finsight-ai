import pandas as pd
import numpy as np
import os
import json
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

PROCESSED_DIR = "data/processed/"
MODELS_DIR    = "data/models/"
os.makedirs(MODELS_DIR, exist_ok=True)

FEATURE_COLS = [
    "MA_7", "MA_30", "MA_90",
    "Return_1d", "Return_7d", "Return_30d",
    "Volatility_7d", "Volatility_30d",
    "Volume_Ratio", "RSI_14",
    "Price_above_MA30", "Price_above_MA90", "MA_cross",
    "profit_margins", "debt_to_equity", "operating_margins",
    "earnings_growth", "revenue_growth", "current_ratio",
    "return_on_equity", "financial_health_score"
]


def prepare_xy(df: pd.DataFrame, horizon: int = 3):
    df = df.copy()
    future_return = df["Close"].shift(-horizon) / df["Close"] - 1
    df["Target"]  = (future_return > 0).astype(int)
    df = df.dropna(subset=["Target"] + FEATURE_COLS)
    X  = df[FEATURE_COLS]
    y  = df["Target"]

    # print class balance so we can see what we're dealing with
    up   = int(y.sum())
    down = int((y == 0).sum())
    ratio = round(down / (up + 1e-9), 2)
    print(f"   Class balance — Up: {up} | Down: {down} | scale_pos_weight: {ratio}")

    return X, y, df, ratio


def train_forecaster(ticker: str, horizon: int = 3):
    path = f"{PROCESSED_DIR}{ticker}_features.csv"
    df   = pd.read_csv(path)
    X, y, _, ratio = prepare_xy(df, horizon=horizon)

    print(f"\n📊 Training direction classifier for {ticker}")
    print(f"   Samples: {len(X)} | Horizon: {horizon} days")

    tscv    = TimeSeriesSplit(n_splits=5)
    metrics = []

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = XGBClassifier(
            n_estimators     = 300,
            learning_rate    = 0.05,
            max_depth        = 4,
            subsample        = 0.8,
            colsample_bytree = 0.8,
            scale_pos_weight = ratio,
            eval_metric      = "auc",
            random_state     = 42,
            verbosity        = 0
        )
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

        preds     = model.predict(X_val)
        acc       = accuracy_score(y_val, preds)
        precision = precision_score(y_val, preds, zero_division=0)
        recall    = recall_score(y_val, preds, zero_division=0)
        f1        = f1_score(y_val, preds, zero_division=0)

        metrics.append({"fold": fold+1, "accuracy": acc,
                        "precision": precision, "recall": recall, "f1": f1})
        print(f"   Fold {fold+1} → Acc: {acc:.3f} | Precision: {precision:.3f} "
              f"| Recall: {recall:.3f} | F1: {f1:.3f}")

    # Final model on all data
    final_model = XGBClassifier(
        n_estimators     = 300,
        learning_rate    = 0.05,
        max_depth        = 4,
        subsample        = 0.8,
        colsample_bytree = 0.8,
        scale_pos_weight = ratio,
        eval_metric      = "auc",
        random_state     = 42,
        verbosity        = 0
    )
    final_model.fit(X, y)

    model_path = f"{MODELS_DIR}{ticker}_forecaster.joblib"
    joblib.dump(final_model, model_path)

    avg_metrics = {
        "ticker"        : ticker,
        "horizon"       : horizon,
        "avg_accuracy"  : round(np.mean([m["accuracy"]  for m in metrics]), 4),
        "avg_precision" : round(np.mean([m["precision"] for m in metrics]), 4),
        "avg_recall"    : round(np.mean([m["recall"]    for m in metrics]), 4),
        "avg_f1"        : round(np.mean([m["f1"]        for m in metrics]), 4),
        "folds"         : metrics
    }
    with open(f"{MODELS_DIR}{ticker}_metrics.json", "w") as f:
        json.dump(avg_metrics, f, indent=2)

    print(f"\n   ✅ Saved → {model_path}")
    print(f"   📈 Avg Accuracy: {avg_metrics['avg_accuracy']} "
          f"| Avg F1: {avg_metrics['avg_f1']}")

    return final_model, avg_metrics


def predict(ticker: str, horizon: int = 3) -> dict:
    model_path = f"{MODELS_DIR}{ticker}_forecaster.joblib"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No trained model for {ticker}. Train first.")

    model = joblib.load(model_path)
    df    = pd.read_csv(f"{PROCESSED_DIR}{ticker}_features.csv")
    X, _, _, _ = prepare_xy(df, horizon=horizon)

    X_latest     = X.iloc[[-1]]
    direction    = model.predict(X_latest)[0]
    proba        = model.predict_proba(X_latest)[0]
    confidence   = round(float(max(proba)) * 100, 1)
    current_price = df["Close"].iloc[-1]

    with open(f"{MODELS_DIR}{ticker}_metrics.json") as f:
        metrics = json.load(f)

    result = {
        "ticker"        : ticker,
        "horizon_days"  : horizon,
        "current_price" : round(float(current_price), 2),
        "direction"     : "UP 📈" if direction == 1 else "DOWN 📉",
        "confidence_pct": confidence,
        "avg_accuracy"  : metrics["avg_accuracy"],
        "avg_f1"        : metrics["avg_f1"],
    }
    return result


if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "INFY", "TCS.NS", "TSLA"]
    results = []

    for t in tickers:
        try:
            train_forecaster(t, horizon=3)
            pred = predict(t, horizon=3)
            results.append(pred)
        except Exception as e:
            print(f"❌ Failed for {t}: {e}")

    print("\n\n=== SUMMARY ===")
    print(f"{'Ticker':<10} {'Direction':<12} {'Confidence':>12} "
          f"{'Accuracy':>10} {'F1':>8}")
    print("-" * 56)
    for r in results:
        print(f"{r['ticker']:<10} {r['direction']:<12} "
              f"{r['confidence_pct']:>10}% "
              f"{r['avg_accuracy']:>10} "
              f"{r['avg_f1']:>8}")