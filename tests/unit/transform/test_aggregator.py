import pandas as pd
import pytest

from finstream.transform.aggregator import Aggregator


class TestAggregator:
    """Unit tests for Aggregator."""

    def test_one_row_per_entity(self, valid_transactions_df: pd.DataFrame) -> None:
        # valid_transactions_df has entities: E001, E002, E001, E003, E002
        result = Aggregator().transform(valid_transactions_df)
        assert len(result) == 3  # E001, E002, E003

    def test_amounts_are_summed_per_entity(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        result = Aggregator().transform(valid_transactions_df)
        e001_amount = result[result["entity"] == "E001"]["amount"].iloc[0]
        # E001 appears at rows 0 (100.0) and 2 (1000.0) → 1100.0
        assert e001_amount == pytest.approx(1100.0)

    def test_result_has_entity_and_amount_columns(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        result = Aggregator().transform(valid_transactions_df)
        assert "entity" in result.columns
        assert "amount" in result.columns

    def test_total_amount_preserved(self, valid_transactions_df: pd.DataFrame) -> None:
        original_total = valid_transactions_df["amount"].sum()
        result = Aggregator().transform(valid_transactions_df)
        assert result["amount"].sum() == pytest.approx(original_total)

    def test_empty_dataframe_returns_empty(self) -> None:
        empty = pd.DataFrame(columns=["entity", "amount"])
        result = Aggregator().transform(empty)
        assert result.empty

    def test_single_entity_returns_one_row(self) -> None:
        df = pd.DataFrame({
            "id": ["tx-1", "tx-2"], "amount": [100.0, 200.0],
            "currency": ["EUR", "EUR"], "entity": ["E001", "E001"],
            "date": pd.to_datetime(["2024-01-15", "2024-01-15"]),
            "source": ["test", "test"],
        })
        result = Aggregator().transform(df)
        assert len(result) == 1
        assert result.iloc[0]["amount"] == pytest.approx(300.0)

    def test_transformer_name_is_not_empty(self) -> None:
        assert Aggregator().transformer_name() != ""
