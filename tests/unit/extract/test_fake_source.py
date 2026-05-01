"""Unit tests for FakeDataSource."""
from datetime import date

import pandas as pd
import pytest

from finstream.extract.fake_source import FakeDataSource


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "id":       [f"tx-{i:03d}" for i in range(10)],
        "amount":   [float(100 + i) for i in range(10)],
        "currency": ["EUR"] * 10,
        "entity":   ["A"] * 10,
        "date":     ["2024-01-15"] * 10,
        "source":   ["fake"] * 10,
    })


BUSINESS_DATE = date(2024, 1, 15)


class TestFakeSourceAvailability:
    def test_is_always_available(self, sample_df: pd.DataFrame) -> None:
        source = FakeDataSource(sample_df)
        assert source.is_available() is True


class TestFakeSourceChunks:
    def test_yields_all_rows_in_one_chunk_when_small(self, sample_df: pd.DataFrame) -> None:
        source = FakeDataSource(sample_df)
        chunks = list(source.read_chunks(BUSINESS_DATE, chunk_size=100))
        assert len(chunks) == 1
        assert len(chunks[0]) == 10

    def test_yields_multiple_chunks_when_large(self, sample_df: pd.DataFrame) -> None:
        source = FakeDataSource(sample_df)
        chunks = list(source.read_chunks(BUSINESS_DATE, chunk_size=3))
        assert len(chunks) == 4

    def test_total_rows_across_chunks_equals_original(self, sample_df: pd.DataFrame) -> None:
        source = FakeDataSource(sample_df)
        chunks = list(source.read_chunks(BUSINESS_DATE, chunk_size=3))
        total = sum(len(c) for c in chunks)
        assert total == len(sample_df)

    def test_empty_dataframe_yields_no_chunks(self) -> None:
        empty = pd.DataFrame(columns=["id", "amount", "currency", "entity", "date", "source"])
        source = FakeDataSource(empty)
        chunks = list(source.read_chunks(BUSINESS_DATE))
        assert chunks == []

    def test_chunks_are_independent_copies(self, sample_df: pd.DataFrame) -> None:
        source = FakeDataSource(sample_df)
        chunks = list(source.read_chunks(BUSINESS_DATE, chunk_size=5))
        chunks[0].loc[0, "amount"] = 99999.0
        assert sample_df.loc[0, "amount"] != 99999.0
