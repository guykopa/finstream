"""Yahoo Finance REST API data source — live market data via HTTP."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Iterator

import httpx
import pandas as pd

from finstream.domain.exceptions import DataSourceUnavailableError
from finstream.interfaces.i_data_source import IDataSource

_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
_HEADERS = {"User-Agent": "Mozilla/5.0"}

# Default tickers: US tech + US finance + CAC 40 blue chips
DEFAULT_TICKERS: dict[str, str] = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "NVDA": "Nvidia",
    "META": "Meta",
    "JPM": "JPMorgan",
    "GS": "Goldman Sachs",
    "MC.PA": "LVMH",
    "AIR.PA": "Airbus",
    "TTE.PA": "TotalEnergies",
    "SAN.PA": "Sanofi",
}


class YahooFinanceAPISource(IDataSource):
    """Fetch live daily market data from Yahoo Finance REST API.

    Each call to read_chunks fetches one year of history for each
    ticker, filters for the requested business date, and yields
    the result as a single DataFrame chunk.
    """

    def __init__(
        self,
        tickers: dict[str, str] | list[str] | None = None,
        timeout: float = 15.0,
    ) -> None:
        if tickers is None:
            self._tickers = DEFAULT_TICKERS
        elif isinstance(tickers, list):
            self._tickers = {t: t for t in tickers}
        else:
            self._tickers = tickers
        self._timeout = timeout

    def read_chunks(
        self,
        business_date: date,
        chunk_size: int = 10_000,
    ) -> Iterator[pd.DataFrame]:
        """Fetch market data for business_date from Yahoo Finance.

        Args:
            business_date: The trading day to fetch.
            chunk_size: Not used (all tickers fit in one chunk).

        Yields:
            One DataFrame with all tickers for the requested date.

        Raises:
            DataSourceUnavailableError: if Yahoo Finance is unreachable.
        """
        target = business_date.isoformat()
        rows: list[dict] = []

        try:
            with httpx.Client(timeout=self._timeout, headers=_HEADERS) as client:
                for ticker, name in self._tickers.items():
                    resp = client.get(
                        f"{_BASE_URL}/{ticker}",
                        params={"range": "1y", "interval": "1d"},
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    result = data.get("chart", {}).get("result")
                    if not result:
                        continue

                    meta = result[0]["meta"]
                    timestamps = result[0].get("timestamp", [])
                    quotes = result[0]["indicators"]["quote"][0]
                    closes = quotes.get("close", [])
                    volumes = quotes.get("volume", [])

                    for ts, close, volume in zip(timestamps, closes, volumes):
                        if close is None or volume is None:
                            continue
                        row_date = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                        if row_date != target:
                            continue
                        rows.append({
                            "id":       f"{ticker}-{row_date}",
                            "amount":   round(close * volume / 1_000_000, 2),
                            "currency": meta.get("currency", "USD"),
                            "entity":   name,
                            "date":     row_date,
                            "source":   "yahoo_finance_live",
                        })

        except httpx.HTTPError as exc:
            raise DataSourceUnavailableError(_BASE_URL) from exc

        if rows:
            yield pd.DataFrame(rows)

    def is_available(self) -> bool:
        """Return True if Yahoo Finance API is reachable."""
        try:
            with httpx.Client(timeout=self._timeout, headers=_HEADERS) as client:
                resp = client.get(f"{_BASE_URL}/AAPL", params={"range": "1d", "interval": "1d"})
                return resp.is_success
        except httpx.HTTPError:
            return False
