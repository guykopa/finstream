"""Unit tests for DataCleaner — RED phase written before implementation."""
import pandas as pd
import pytest

from finstream.transform.data_cleaner import DataCleaner


@pytest.fixture
def cleaner() -> DataCleaner:
    return DataCleaner()


@pytest.fixture
def clean_df() -> pd.DataFrame:
    return pd.DataFrame({
        "id":       ["tx-001", "tx-002", "tx-003"],
        "amount":   [100.0, 200.0, 300.0],
        "currency": ["EUR", "USD", "GBP"],
        "entity":   ["A", "B", "C"],
        "date":     ["2024-01-15", "2024-01-15", "2024-01-15"],
        "source":   ["csv", "csv", "csv"],
    })


class TestDataCleanerName:
    def test_transformer_name(self, cleaner: DataCleaner) -> None:
        assert cleaner.transformer_name() == "DataCleaner"


class TestDataCleanerNegativeAmounts:
    def test_removes_negative_amount_rows(self, cleaner: DataCleaner) -> None:
        df = pd.DataFrame({
            "id":       ["tx-001", "tx-002"],
            "amount":   [100.0, -50.0],
            "currency": ["EUR", "EUR"],
            "entity":   ["A", "B"],
            "date":     ["2024-01-15", "2024-01-15"],
            "source":   ["csv", "csv"],
        })
        result = cleaner.transform(df)
        assert len(result) == 1
        assert result.iloc[0]["id"] == "tx-001"

    def test_removes_zero_amount_rows(self, cleaner: DataCleaner) -> None:
        df = pd.DataFrame({
            "id":       ["tx-001", "tx-002"],
            "amount":   [100.0, 0.0],
            "currency": ["EUR", "EUR"],
            "entity":   ["A", "B"],
            "date":     ["2024-01-15", "2024-01-15"],
            "source":   ["csv", "csv"],
        })
        result = cleaner.transform(df)
        assert len(result) == 1

    def test_keeps_positive_amounts(self, cleaner: DataCleaner, clean_df: pd.DataFrame) -> None:
        result = cleaner.transform(clean_df)
        assert len(result) == len(clean_df)


class TestDataCleanerInvalidCurrencies:
    def test_removes_unknown_currency_rows(self, cleaner: DataCleaner) -> None:
        df = pd.DataFrame({
            "id":       ["tx-001", "tx-002"],
            "amount":   [100.0, 200.0],
            "currency": ["EUR", "XYZ"],
            "entity":   ["A", "B"],
            "date":     ["2024-01-15", "2024-01-15"],
            "source":   ["csv", "csv"],
        })
        result = cleaner.transform(df)
        assert len(result) == 1
        assert result.iloc[0]["currency"] == "EUR"

    def test_keeps_null_currency_rows_for_quality_rules(self, cleaner: DataCleaner) -> None:
        df = pd.DataFrame({
            "id":       ["tx-001", "tx-002"],
            "amount":   [100.0, 200.0],
            "currency": ["EUR", None],
            "entity":   ["A", "B"],
            "date":     ["2024-01-15", "2024-01-15"],
            "source":   ["csv", "csv"],
        })
        result = cleaner.transform(df)
        assert len(result) == 2

    def test_keeps_all_valid_currencies(self, cleaner: DataCleaner) -> None:
        df = pd.DataFrame({
            "id":       ["t1", "t2", "t3", "t4"],
            "amount":   [100.0, 200.0, 300.0, 400.0],
            "currency": ["EUR", "USD", "GBP", "CHF"],
            "entity":   ["A", "B", "C", "D"],
            "date":     ["2024-01-15"] * 4,
            "source":   ["csv"] * 4,
        })
        result = cleaner.transform(df)
        assert len(result) == 4


class TestDataCleanerCombined:
    def test_removes_multiple_bad_rows(self, cleaner: DataCleaner) -> None:
        df = pd.DataFrame({
            "id":       ["tx-001", "tx-002", "tx-003", "tx-004"],
            "amount":   [100.0, -50.0, 200.0, 300.0],
            "currency": ["EUR", "EUR", "XYZ", "USD"],
            "entity":   ["A", "B", "C", "D"],
            "date":     ["2024-01-15"] * 4,
            "source":   ["csv"] * 4,
        })
        result = cleaner.transform(df)
        assert len(result) == 2
        assert list(result["id"]) == ["tx-001", "tx-004"]

    def test_empty_dataframe_returns_empty(self, cleaner: DataCleaner) -> None:
        df = pd.DataFrame(columns=["id", "amount", "currency", "entity", "date", "source"])
        result = cleaner.transform(df)
        assert len(result) == 0

    def test_all_rows_bad_returns_empty(self, cleaner: DataCleaner) -> None:
        df = pd.DataFrame({
            "id":       ["tx-001", "tx-002"],
            "amount":   [-100.0, -200.0],
            "currency": ["EUR", "EUR"],
            "entity":   ["A", "B"],
            "date":     ["2024-01-15", "2024-01-15"],
            "source":   ["csv", "csv"],
        })
        result = cleaner.transform(df)
        assert len(result) == 0

    def test_index_is_reset_after_cleaning(self, cleaner: DataCleaner) -> None:
        df = pd.DataFrame({
            "id":       ["tx-001", "tx-002", "tx-003"],
            "amount":   [-10.0, 100.0, 200.0],
            "currency": ["EUR", "EUR", "USD"],
            "entity":   ["A", "B", "C"],
            "date":     ["2024-01-15"] * 3,
            "source":   ["csv"] * 3,
        })
        result = cleaner.transform(df)
        assert list(result.index) == list(range(len(result)))

    def test_does_not_modify_original_dataframe(self, cleaner: DataCleaner) -> None:
        df = pd.DataFrame({
            "id":       ["tx-001", "tx-002"],
            "amount":   [100.0, -50.0],
            "currency": ["EUR", "EUR"],
            "entity":   ["A", "B"],
            "date":     ["2024-01-15", "2024-01-15"],
            "source":   ["csv", "csv"],
        })
        original_len = len(df)
        cleaner.transform(df)
        assert len(df) == original_len
