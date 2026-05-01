import pandas as pd
import pytest

from finstream.bigdata.memory_optimizer import MemoryOptimizer


class TestMemoryOptimizer:
    """Unit tests for MemoryOptimizer."""

    def test_float64_columns_downcast_to_float32(self) -> None:
        df = pd.DataFrame({"amount": pd.array([1.0, 2.0, 3.0], dtype="float64")})
        result = MemoryOptimizer().optimize(df)
        assert result["amount"].dtype == "float32"

    def test_low_cardinality_object_columns_become_category(self) -> None:
        df = pd.DataFrame({
            "currency": ["EUR", "USD", "EUR", "GBP"] * 100,
        })
        result = MemoryOptimizer().optimize(df)
        assert str(result["currency"].dtype) == "category"

    def test_high_cardinality_object_columns_stay_object(self) -> None:
        # id has 1000 unique values out of 1000 → not worth categorizing
        df = pd.DataFrame({
            "id": [f"tx-{i}" for i in range(1000)],
        })
        result = MemoryOptimizer().optimize(df)
        assert result["id"].dtype == object

    def test_memory_usage_is_reduced(self, large_df: pd.DataFrame) -> None:
        before = large_df.memory_usage(deep=True).sum()
        result = MemoryOptimizer().optimize(large_df)
        after = result.memory_usage(deep=True).sum()
        assert after < before

    def test_values_are_preserved_after_optimization(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        result = MemoryOptimizer().optimize(valid_transactions_df)
        assert list(result["id"]) == list(valid_transactions_df["id"])
        assert result["amount"].tolist() == pytest.approx(
            valid_transactions_df["amount"].tolist(), rel=1e-5
        )

    def test_row_count_unchanged(self, valid_transactions_df: pd.DataFrame) -> None:
        result = MemoryOptimizer().optimize(valid_transactions_df)
        assert len(result) == len(valid_transactions_df)

    def test_empty_dataframe_returns_empty(self) -> None:
        empty = pd.DataFrame(columns=["amount", "currency"])
        result = MemoryOptimizer().optimize(empty)
        assert result.empty
