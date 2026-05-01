import pandas as pd
import pytest

from finstream.transform.currency_normalizer import CurrencyNormalizer

# Taux fixes injectés pour que les tests soient déterministes
RATES = {"EUR": 1.0, "USD": 0.5, "GBP": 2.0, "CHF": 1.0}


class TestCurrencyNormalizer:
    """Unit tests for CurrencyNormalizer."""

    def test_eur_amount_unchanged(self) -> None:
        df = pd.DataFrame({
            "id": ["tx-1"], "amount": [100.0], "currency": ["EUR"],
            "entity": ["E1"], "date": pd.to_datetime(["2024-01-15"]),
            "source": ["test"],
        })
        result = CurrencyNormalizer(rates=RATES).transform(df)
        assert result.loc[0, "amount"] == pytest.approx(100.0)
        assert result.loc[0, "currency"] == "EUR"

    def test_usd_converted_to_eur(self) -> None:
        df = pd.DataFrame({
            "id": ["tx-1"], "amount": [200.0], "currency": ["USD"],
            "entity": ["E1"], "date": pd.to_datetime(["2024-01-15"]),
            "source": ["test"],
        })
        result = CurrencyNormalizer(rates=RATES).transform(df)
        assert result.loc[0, "amount"] == pytest.approx(100.0)
        assert result.loc[0, "currency"] == "EUR"

    def test_gbp_converted_to_eur(self) -> None:
        df = pd.DataFrame({
            "id": ["tx-1"], "amount": [50.0], "currency": ["GBP"],
            "entity": ["E1"], "date": pd.to_datetime(["2024-01-15"]),
            "source": ["test"],
        })
        result = CurrencyNormalizer(rates=RATES).transform(df)
        assert result.loc[0, "amount"] == pytest.approx(100.0)
        assert result.loc[0, "currency"] == "EUR"

    def test_all_currencies_become_eur(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        result = CurrencyNormalizer(rates=RATES).transform(valid_transactions_df)
        assert (result["currency"] == "EUR").all()

    def test_row_count_unchanged(self, valid_transactions_df: pd.DataFrame) -> None:
        result = CurrencyNormalizer(rates=RATES).transform(valid_transactions_df)
        assert len(result) == len(valid_transactions_df)

    def test_raises_on_unknown_currency(self) -> None:
        df = pd.DataFrame({
            "id": ["tx-1"], "amount": [100.0], "currency": ["XYZ"],
            "entity": ["E1"], "date": pd.to_datetime(["2024-01-15"]),
            "source": ["test"],
        })
        with pytest.raises(Exception):
            CurrencyNormalizer(rates=RATES).transform(df)

    def test_transformer_name_is_not_empty(self) -> None:
        assert CurrencyNormalizer(rates=RATES).transformer_name() != ""
