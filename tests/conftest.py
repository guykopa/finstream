from datetime import date, datetime
from typing import Iterator

import numpy as np
import pandas as pd
import pytest

from finstream.domain.models.pipeline_report import PipelineReport, PipelineStatus
from finstream.interfaces.i_data_source import IDataSource
from finstream.interfaces.i_data_storage import IDataStorage


# ---------------------------------------------------------------------------
# DataFrame fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_transactions_df() -> pd.DataFrame:
    """Valid financial transactions DataFrame — all quality rules pass."""
    return pd.DataFrame({
        "id":       ["tx-001", "tx-002", "tx-003", "tx-004", "tx-005"],
        "amount":   [100.0, 250.50, 1000.0, 75.25, 500.0],
        "currency": ["EUR", "USD", "GBP", "EUR", "CHF"],
        "entity":   ["E001", "E002", "E001", "E003", "E002"],
        "date":     pd.to_datetime(["2024-01-15"] * 5),
        "source":   ["postgresql"] * 5,
    })


@pytest.fixture
def df_with_nulls(valid_transactions_df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame with null values in required fields (amount, currency)."""
    df = valid_transactions_df.copy()
    df.loc[0, "amount"] = None
    df.loc[2, "currency"] = None
    return df


@pytest.fixture
def df_with_negative_amounts(valid_transactions_df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame containing negative amount values."""
    df = valid_transactions_df.copy()
    df.loc[1, "amount"] = -50.0
    df.loc[3, "amount"] = -100.0
    return df


@pytest.fixture
def df_with_duplicates(valid_transactions_df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame with a duplicate transaction id."""
    duplicate = valid_transactions_df.iloc[0:1].copy()
    return pd.concat([valid_transactions_df, duplicate], ignore_index=True)


@pytest.fixture
def df_with_invalid_currencies(valid_transactions_df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame with unsupported ISO currency codes."""
    df = valid_transactions_df.copy()
    df.loc[0, "currency"] = "INVALID"
    df.loc[2, "currency"] = "XYZ"
    return df


@pytest.fixture
def df_with_future_dates(valid_transactions_df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame with dates set in the future."""
    df = valid_transactions_df.copy()
    df.loc[0, "date"] = pd.Timestamp("2099-01-01")
    return df


@pytest.fixture
def df_with_old_dates(valid_transactions_df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame with dates older than 5 years."""
    df = valid_transactions_df.copy()
    df.loc[0, "date"] = pd.Timestamp("2000-01-01")
    return df


@pytest.fixture
def large_df() -> pd.DataFrame:
    """Large DataFrame for Big Data chunking tests (100k rows)."""
    rng = np.random.default_rng(seed=42)
    n = 100_000
    return pd.DataFrame({
        "id":       [f"tx-{i:08d}" for i in range(n)],
        "amount":   rng.uniform(1.0, 10_000.0, n),
        "currency": rng.choice(["EUR", "USD", "GBP", "CHF"], n),
        "entity":   [f"E{i % 100:03d}" for i in range(n)],
        "date":     pd.to_datetime(["2024-01-15"] * n),
        "source":   ["test"] * n,
    })


# ---------------------------------------------------------------------------
# PipelineReport fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_pipeline_report() -> PipelineReport:
    """A completed pipeline report for report generation tests."""
    return PipelineReport(
        run_id="run-abc-123",
        date=date(2024, 1, 15),
        total_records=50_000,
        clean_records=49_500,
        quality_score=100.0,
        duration_seconds=12.4,
        chunk_count=5,
        memory_peak_mb=210.5,
        status=PipelineStatus.COMPLETED,
        started_at=datetime(2024, 1, 15, 8, 0, 0),
    )


# ---------------------------------------------------------------------------
# Fake adapters — replace real PostgreSQL / storage in unit tests
# ---------------------------------------------------------------------------

class FakeDataSource(IDataSource):
    """In-memory data source for unit tests — no real database needed."""

    def __init__(self, df: pd.DataFrame, chunk_size: int = 10_000) -> None:
        self._df = df
        self._chunk_size = chunk_size

    def read_chunks(
        self,
        business_date: date,
        chunk_size: int = 10_000,
    ) -> Iterator[pd.DataFrame]:
        size = chunk_size or self._chunk_size
        for start in range(0, len(self._df), size):
            yield self._df.iloc[start : start + size].copy()

    def is_available(self) -> bool:
        return True


class FakeDataStorage(IDataStorage):
    """In-memory storage for unit tests — captures written chunks."""

    def __init__(self) -> None:
        self.written_chunks: list[pd.DataFrame] = []

    def write_chunk(self, df: pd.DataFrame, table: str) -> None:
        self.written_chunks.append(df.copy())

    def total_records_written(self) -> int:
        return sum(len(df) for df in self.written_chunks)

    def is_available(self) -> bool:
        return True


@pytest.fixture
def fake_source(valid_transactions_df: pd.DataFrame) -> FakeDataSource:
    """FakeDataSource pre-loaded with valid transactions."""
    return FakeDataSource(valid_transactions_df)


@pytest.fixture
def fake_storage() -> FakeDataStorage:
    """Empty FakeDataStorage ready to capture writes."""
    return FakeDataStorage()
