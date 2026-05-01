"""Unit tests for YahooFinanceAPISource — mocked HTTP, no real network calls."""
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from finstream.domain.exceptions import DataSourceUnavailableError
from finstream.extract.yahoo_finance_api_source import YahooFinanceAPISource

_FAKE_RESPONSE = {
    "chart": {
        "result": [{
            "meta": {"symbol": "AAPL", "currency": "USD"},
            "timestamp": [1705276800, 1705363200],
            "indicators": {
                "quote": [{
                    "close":  [185.0, 186.0],
                    "volume": [50_000_000, 45_000_000],
                }]
            },
        }],
        "error": None,
    }
}


@pytest.fixture
def source():
    return YahooFinanceAPISource(tickers=["AAPL", "MSFT"])


def _mock_client(json_data: dict):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    client = MagicMock()
    client.__enter__ = MagicMock(return_value=client)
    client.__exit__ = MagicMock(return_value=False)
    client.get.return_value = resp
    return client


class TestYahooFinanceAPISource:
    def test_yields_dataframe_for_date(self, source):
        with patch("httpx.Client", return_value=_mock_client(_FAKE_RESPONSE)):
            chunks = list(source.read_chunks(date(2024, 1, 15)))
        assert len(chunks) > 0
        assert not chunks[0].empty

    def test_dataframe_has_required_columns(self, source):
        with patch("httpx.Client", return_value=_mock_client(_FAKE_RESPONSE)):
            chunks = list(source.read_chunks(date(2024, 1, 15)))
        cols = set(chunks[0].columns)
        assert {"id", "amount", "currency", "entity", "date", "source"}.issubset(cols)

    def test_currency_is_usd_for_us_tickers(self, source):
        with patch("httpx.Client", return_value=_mock_client(_FAKE_RESPONSE)):
            chunks = list(source.read_chunks(date(2024, 1, 15)))
        assert all(chunks[0]["currency"] == "USD")

    def test_source_column_is_yahoo_finance_live(self, source):
        with patch("httpx.Client", return_value=_mock_client(_FAKE_RESPONSE)):
            chunks = list(source.read_chunks(date(2024, 1, 15)))
        assert all(chunks[0]["source"] == "yahoo_finance_live")

    def test_raises_on_http_error(self, source):
        import httpx
        client = MagicMock()
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)
        client.get.side_effect = httpx.HTTPError("connection error")
        with patch("httpx.Client", return_value=client):
            with pytest.raises(DataSourceUnavailableError):
                list(source.read_chunks(date(2024, 1, 15)))

    def test_is_available_returns_true_on_success(self, source):
        resp = MagicMock()
        resp.is_success = True
        client = MagicMock()
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)
        client.get.return_value = resp
        with patch("httpx.Client", return_value=client):
            assert source.is_available() is True

    def test_is_available_returns_false_on_error(self, source):
        import httpx
        client = MagicMock()
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)
        client.get.side_effect = httpx.HTTPError("timeout")
        with patch("httpx.Client", return_value=client):
            assert source.is_available() is False
