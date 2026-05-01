import pandas as pd
import pytest

from finstream.transform.deduplicator import Deduplicator


class TestDeduplicator:
    """Unit tests for Deduplicator."""

    def test_no_change_on_unique_ids(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        result = Deduplicator().transform(valid_transactions_df)
        assert len(result) == len(valid_transactions_df)

    def test_removes_duplicate_rows(self, df_with_duplicates: pd.DataFrame) -> None:
        original_unique = df_with_duplicates["id"].nunique()
        result = Deduplicator().transform(df_with_duplicates)
        assert len(result) == original_unique

    def test_keeps_first_occurrence(self, valid_transactions_df: pd.DataFrame) -> None:
        duplicate = valid_transactions_df.copy()
        duplicate.loc[0, "amount"] = 9999.0
        df = pd.concat([valid_transactions_df, duplicate], ignore_index=True)
        result = Deduplicator().transform(df)
        # first occurrence of tx-001 has amount=100.0, not 9999.0
        first_row = result[result["id"] == "tx-001"].iloc[0]
        assert first_row["amount"] == pytest.approx(100.0)

    def test_empty_dataframe_returns_empty(self) -> None:
        empty = pd.DataFrame(columns=["id", "amount", "currency"])
        result = Deduplicator().transform(empty)
        assert result.empty

    def test_columns_unchanged(self, valid_transactions_df: pd.DataFrame) -> None:
        result = Deduplicator().transform(valid_transactions_df)
        assert list(result.columns) == list(valid_transactions_df.columns)

    def test_transformer_name_is_not_empty(self) -> None:
        assert Deduplicator().transformer_name() != ""
