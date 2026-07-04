import yfinance as yf
import pandas as pd
import os

def fetch_stock_data(ticker: str, period: str = "5y") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    hist.reset_index(inplace=True)
    return hist

def fetch_fundamentals(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    info = stock.info
    fundamentals = {
        "ticker": ticker,
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "revenue": info.get("totalRevenue"),
        "profit_margins": info.get("profitMargins"),
        "debt_to_equity": info.get("debtToEquity"),
        "operating_margins": info.get("operatingMargins"),
        "earnings_growth": info.get("earningsGrowth"),
        "revenue_growth": info.get("revenueGrowth"),
        "current_ratio": info.get("currentRatio"),
        "return_on_equity": info.get("returnOnEquity"),
    }
    return fundamentals

def save_data(ticker: str, output_dir: str = "data/raw/"):
    os.makedirs(output_dir, exist_ok=True)
    hist = fetch_stock_data(ticker)
    hist.to_csv(f"{output_dir}{ticker}_prices.csv", index=False)
    print(f"✅ Saved price data for {ticker}")
    fund = fetch_fundamentals(ticker)
    fund_df = pd.DataFrame([fund])
    fund_df.to_csv(f"{output_dir}{ticker}_fundamentals.csv", index=False)
    print(f"✅ Saved fundamentals for {ticker}")

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "INFY", "TCS.NS", "TSLA"]
    for t in tickers:
        try:
            save_data(t)
        except Exception as e:
            print(f"❌ Failed for {t}: {e}")