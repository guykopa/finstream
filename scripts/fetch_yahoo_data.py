"""Download real stock data from Yahoo Finance and format it for finstream."""
import pandas as pd
import yfinance as yf

TICKERS = {
    # US Tech
    "AAPL":  "Apple",
    "MSFT":  "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN":  "Amazon",
    "NVDA":  "Nvidia",
    "META":  "Meta",
    "TSLA":  "Tesla",
    # US Finance
    "JPM":   "JPMorgan",
    "GS":    "Goldman Sachs",
    "MS":    "Morgan Stanley",
    "BAC":   "Bank of America",
    # Europe (CAC 40 / Euronext)
    "MC.PA": "LVMH",
    "AI.PA": "Air Liquide",
    "TTE.PA":"TotalEnergies",
    "SAN.PA":"Sanofi",
    "AIR.PA":"Airbus",
    "BNP.PA":"BNP Paribas",
    "OR.PA": "L'Oréal",
    "SU.PA": "Schneider Electric",
    "RI.PA": "Pernod Ricard",
}

QUARTERS = [
    ("2024-01-01", "2024-03-31", "Q1"),
    ("2024-04-01", "2024-06-30", "Q2"),
    ("2024-07-01", "2024-09-30", "Q3"),
    ("2024-10-01", "2024-12-31", "Q4"),
]

for start, end, label in QUARTERS:
    rows = []
    print(f"\n=== {label} ({start} → {end}) ===")

    for ticker, name in TICKERS.items():
        try:
            df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
            if df.empty:
                print(f"  {ticker}: no data")
                continue
            for i, (ts, row) in enumerate(df.iterrows()):
                close  = float(row["Close"].iloc[0])  if hasattr(row["Close"],  "iloc") else float(row["Close"])
                volume = float(row["Volume"].iloc[0]) if hasattr(row["Volume"], "iloc") else float(row["Volume"])
                rows.append({
                    "id":       f"{ticker}-{ts.strftime('%Y%m%d')}",
                    "amount":   round(close * volume / 1_000_000, 2),
                    "currency": "EUR" if ".PA" in ticker else "USD",
                    "entity":   name,
                    "date":     ts.strftime("%Y-%m-%d"),
                    "source":   "yahoo_finance",
                })
            print(f"  {ticker}: {len(df)} jours")
        except Exception as e:
            print(f"  {ticker}: erreur — {e}")

    df_out = pd.DataFrame(rows)
    path = f"data/transactions_yahoo_2024_{label}.csv"
    df_out.to_csv(path, index=False)
    print(f"→ {len(df_out)} transactions sauvegardées dans {path}")
