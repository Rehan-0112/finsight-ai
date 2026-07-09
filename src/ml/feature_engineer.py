import pandas as pd
import numpy as np
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_DIR = "data/raw/"
PROCESSED_DIR = "data/processed/"
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ── Price Feature Engineering ─────────────────────────────────────────────────
def engineer_price_features(ticker: str) -> pd.DataFrame:
    """
    Load raw price CSV and build technical + trend features.
    """
    path = f"{RAW_DIR}{ticker}_prices.csv"
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], utc=True)
    df = df.sort_values("Date").reset_index(drop=True)

    # ── Moving averages
    df["MA_7"]  = df["Close"].rolling(window=7).mean()
    df["MA_30"] = df["Close"].rolling(window=30).mean()
    df["MA_90"] = df["Close"].rolling(window=90).mean()

    # ── Price momentum
    df["Return_1d"]  = df["Close"].pct_change(1)
    df["Return_7d"]  = df["Close"].pct_change(7)
    df["Return_30d"] = df["Close"].pct_change(30)

    # ── Volatility (rolling std of daily returns)
    df["Volatility_7d"]  = df["Return_1d"].rolling(7).std()
    df["Volatility_30d"] = df["Return_1d"].rolling(30).std()

    # ── Volume trend
    df["Volume_MA7"]   = df["Volume"].rolling(7).mean()
    df["Volume_Ratio"] = df["Volume"] / df["Volume_MA7"]

    # ── RSI (14-day)
    delta = df["Close"].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / (loss + 1e-9)
    df["RSI_14"] = 100 - (100 / (1 + rs))

    # ── Price vs moving average signals
    df["Price_above_MA30"] = (df["Close"] > df["MA_30"]).astype(int)
    df["Price_above_MA90"] = (df["Close"] > df["MA_90"]).astype(int)
    df["MA_cross"]         = (df["MA_7"] > df["MA_30"]).astype(int)

    # ── Drop NaNs from rolling windows
    df = df.dropna().reset_index(drop=True)

    return df


# ── Fundamental Feature Engineering ──────────────────────────────────────────
def engineer_fundamental_features(ticker: str) -> pd.DataFrame:
    """
    Load raw fundamentals CSV and build ratio-based features.
    """
    path = f"{RAW_DIR}{ticker}_fundamentals.csv"
    df = pd.read_csv(path)

    # ── Profitability ratios
    df["profit_margin_pct"]    = df["profit_margins"] * 100
    df["operating_margin_pct"] = df["operating_margins"] * 100

    # ── Growth signals
    df["revenue_growth_pct"]  = df["revenue_growth"] * 100
    df["earnings_growth_pct"] = df["earnings_growth"] * 100

    # ── Leverage signal
    df["high_debt"] = (df["debt_to_equity"] > 1.5).astype(int)

    # ── Efficiency signal
    df["strong_roe"] = (df["return_on_equity"] > 0.15).astype(int)

    # ── Liquidity signal
    df["healthy_current_ratio"] = (df["current_ratio"] > 1.5).astype(int)

    # ── Composite health score (simple weighted sum, 0-100)
    df["financial_health_score"] = (
        df["profit_margins"].fillna(0)    * 30 +
        df["return_on_equity"].fillna(0)  * 25 +
        df["revenue_growth"].fillna(0)    * 20 +
        df["current_ratio"].fillna(0)     *  5 -
        df["debt_to_equity"].fillna(0)    * 10
    ).clip(0, 100)

    return df


# ── Merge Price + Fundamentals ────────────────────────────────────────────────
def build_feature_set(ticker: str) -> pd.DataFrame:
    """
    Combine price and fundamental features into one feature set.
    """
    price_df = engineer_price_features(ticker)
    fund_df  = engineer_fundamental_features(ticker)

    # Broadcast fundamentals across all price rows (fundamentals are static per ticker)
    for col in fund_df.columns:
        if col != "ticker":
            price_df[col] = fund_df[col].values[0]

    price_df["ticker"] = ticker

    return price_df


# ── Save Processed Features ───────────────────────────────────────────────────
def save_features(ticker: str):
    df = build_feature_set(ticker)
    out_path = f"{PROCESSED_DIR}{ticker}_features.csv"
    df.to_csv(out_path, index=False)
    print(f"✅ Features saved for {ticker} → {out_path} | Shape: {df.shape}")


# ── Run for all tickers ───────────────────────────────────────────────────────
if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "INFY", "TCS.NS", "TSLA"]

    all_features = []

    for t in tickers:
        try:
            save_features(t)
            all_features.append(pd.read_csv(f"{PROCESSED_DIR}{t}_features.csv"))
        except Exception as e:
            print(f"❌ Failed for {t}: {e}")

    # Save combined dataset
    combined = pd.concat(all_features, ignore_index=True)
    combined.to_csv(f"{PROCESSED_DIR}all_features.csv", index=False)
    print(f"\n✅ Combined dataset saved → {PROCESSED_DIR}all_features.csv")
    print(f"   Total rows: {len(combined)} | Columns: {combined.shape[1]}")
    print(f"\n   Features built: {[c for c in combined.columns if c not in ['Date','ticker']]}")