from datetime import date

import pandas as pd
import pytest

from tests.conftest import FakeDataStorage
from finstream.domain.exceptions import QualityGateError
from finstream.domain.models.pipeline_report import PipelineStatus
from finstream.extract.csv_source import CSVSource
from finstream.pipeline.etl_pipeline import ETLPipeline

BUSINESS_DATE = date(2024, 1, 15)


def make_csv(tmp_path, df: pd.DataFrame) -> str:
    """Write a DataFrame to a temp CSV and return its path."""
    path = tmp_path / "transactions.csv"
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def valid_csv(tmp_path, valid_transactions_df: pd.DataFrame) -> str:
    return make_csv(tmp_path, valid_transactions_df)


@pytest.fixture
def bad_csv(tmp_path, df_with_nulls: pd.DataFrame) -> str:
    return make_csv(tmp_path, df_with_nulls)


class TestETLPipelineIntegration:
    """End-to-end integration tests for ETLPipeline using CSVSource."""

    def test_pipeline_runs_end_to_end(self, valid_csv: str) -> None:
        storage = FakeDataStorage()
        pipeline = ETLPipeline(
            source=CSVSource(valid_csv),
            storage=storage,
        )
        report = pipeline.run(BUSINESS_DATE)
        assert report.status == PipelineStatus.COMPLETED
        assert report.total_records > 0

    def test_all_records_reach_storage(
        self, valid_csv: str, valid_transactions_df: pd.DataFrame
    ) -> None:
        storage = FakeDataStorage()
        pipeline = ETLPipeline(source=CSVSource(valid_csv), storage=storage)
        pipeline.run(BUSINESS_DATE)
        assert storage.total_records_written() == len(valid_transactions_df)

    def test_pipeline_report_has_valid_run_id(self, valid_csv: str) -> None:
        storage = FakeDataStorage()
        report = ETLPipeline(source=CSVSource(valid_csv), storage=storage).run(
            BUSINESS_DATE
        )
        assert report.run_id != ""

    def test_quality_score_is_100_on_clean_data(self, valid_csv: str) -> None:
        storage = FakeDataStorage()
        report = ETLPipeline(source=CSVSource(valid_csv), storage=storage).run(
            BUSINESS_DATE
        )
        assert report.quality_score == 100.0

    def test_pipeline_raises_on_bad_data(self, bad_csv: str) -> None:
        storage = FakeDataStorage()
        pipeline = ETLPipeline(
            source=CSVSource(bad_csv),
            storage=storage,
            quality_gate_threshold=80.0,
        )
        with pytest.raises(QualityGateError):
            pipeline.run(BUSINESS_DATE)

    def test_pipeline_processes_large_csv_in_chunks(self, tmp_path: str) -> None:
        import numpy as np

        rng = np.random.default_rng(42)
        n = 25_000
        df = pd.DataFrame({
            "id":       [f"tx-{i:08d}" for i in range(n)],
            "amount":   rng.uniform(1.0, 1000.0, n),
            "currency": rng.choice(["EUR", "USD", "GBP", "CHF"], n),
            "entity":   [f"E{i % 10:03d}" for i in range(n)],
            "date":     ["2024-01-15"] * n,
            "source":   ["csv"] * n,
        })
        path = make_csv(tmp_path, df)
        storage = FakeDataStorage()
        report = ETLPipeline(
            source=CSVSource(path), storage=storage, chunk_size=10_000
        ).run(BUSINESS_DATE)
        assert report.chunk_count >= 2
        assert storage.total_records_written() == n

    def test_source_unavailable_raises(self) -> None:
        from finstream.domain.exceptions import DataSourceUnavailableError

        storage = FakeDataStorage()
        pipeline = ETLPipeline(
            source=CSVSource("/nonexistent/path.csv"),
            storage=storage,
        )
        with pytest.raises(DataSourceUnavailableError):
            pipeline.run(BUSINESS_DATE)
