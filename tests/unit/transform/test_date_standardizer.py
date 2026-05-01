import pandas as pd
import pytest

from finstream.transform.date_standardizer import DateStandardizer


class TestDateStandardizer:
    """Unit tests for DateStandardizer."""

    def test_date_column_is_datetime(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        result = DateStandardizer().transform(valid_transactions_df)
        assert pd.api.types.is_datetime64_any_dtype(result["date"])

    def test_string_dates_are_parsed(self) -> None:
        df = pd.DataFrame({
            "id": ["tx-1"], "amount": [100.0], "currency": ["EUR"],
            "entity": ["E1"], "date": ["2024-01-15"], "source": ["test"],
        })
        result = DateStandardizer().transform(df)
        assert pd.api.types.is_datetime64_any_dtype(result["date"])

    def test_timezone_aware_dates_are_normalized(self) -> None:
        df = pd.DataFrame({
            "id": ["tx-1"], "amount": [100.0], "currency": ["EUR"],
            "entity": ["E1"],
            "date": pd.to_datetime(["2024-01-15"]).tz_localize("US/Eastern"),
            "source": ["test"],
        })
        result = DateStandardizer().transform(df)
        assert result.loc[0, "date"].tzinfo is None

    def test_row_count_unchanged(self, valid_transactions_df: pd.DataFrame) -> None:
        result = DateStandardizer().transform(valid_transactions_df)
        assert len(result) == len(valid_transactions_df)

    def test_other_columns_unchanged(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        result = DateStandardizer().transform(valid_transactions_df)
        assert list(result["id"]) == list(valid_transactions_df["id"])
        assert list(result["amount"]) == list(valid_transactions_df["amount"])

    def test_empty_dataframe_returns_empty(self) -> None:
        empty = pd.DataFrame(columns=["id", "date"])
        result = DateStandardizer().transform(empty)
        assert result.empty

    def test_transformer_name_is_not_empty(self) -> None:
        assert DateStandardizer().transformer_name() != ""
