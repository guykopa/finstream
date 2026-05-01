"""Non-regression tests — verify pipeline behaviour stays stable across runs."""
from datetime import date

import numpy as np
import pandas as pd

from tests.conftest import FakeDataSource, FakeDataStorage
from finstream.domain.models.pipeline_report import PipelineStatus
from finstream.pipeline.etl_pipeline import ETLPipeline

BUSINESS_DATE = date(2024, 1, 15)


def _make_clean_df(n: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "id":       [f"tx-{i:08d}" for i in range(n)],
        "amount":   rng.uniform(1.0, 5_000.0, n).tolist(),
        "currency": rng.choice(["EUR", "USD", "GBP", "CHF"], n).tolist(),
        "entity":   [f"E{i % 20:03d}" for i in range(n)],
        "date":     ["2024-01-15"] * n,
        "source":   ["test"] * n,
    })


class TestPipelineStability:
    """Verify pipeline correctness and reproducibility."""

    def test_pipeline_completes_on_clean_data(self) -> None:
        storage = FakeDataStorage()
        report = ETLPipeline(
            source=FakeDataSource(_make_clean_df(1_000)),
            storage=storage,
        ).run(BUSINESS_DATE)
        assert report.status == PipelineStatus.COMPLETED

    def test_quality_score_is_100_on_clean_data(self) -> None:
        storage = FakeDataStorage()
        report = ETLPipeline(
            source=FakeDataSource(_make_clean_df(1_000)),
            storage=storage,
        ).run(BUSINESS_DATE)
        assert report.quality_score == 100.0

    def test_all_records_written_to_storage(self) -> None:
        df = _make_clean_df(500)
        storage = FakeDataStorage()
        ETLPipeline(source=FakeDataSource(df), storage=storage).run(BUSINESS_DATE)
        assert storage.total_records_written() == len(df)

    def test_two_runs_with_same_seed_produce_same_record_count(self) -> None:
        s1 = FakeDataStorage()
        s2 = FakeDataStorage()
        ETLPipeline(
            source=FakeDataSource(_make_clean_df(300, seed=7)), storage=s1
        ).run(BUSINESS_DATE)
        ETLPipeline(
            source=FakeDataSource(_make_clean_df(300, seed=7)), storage=s2
        ).run(BUSINESS_DATE)
        assert s1.total_records_written() == s2.total_records_written()

    def test_pipeline_processes_10k_records_without_error(self) -> None:
        storage = FakeDataStorage()
        report = ETLPipeline(
            source=FakeDataSource(_make_clean_df(10_000)),
            storage=storage,
            chunk_size=2_500,
        ).run(BUSINESS_DATE)
        assert report.chunk_count == 4
        assert report.status == PipelineStatus.COMPLETED

    def test_run_id_is_unique_across_runs(self) -> None:
        ids = set()
        for _ in range(5):
            storage = FakeDataStorage()
            report = ETLPipeline(
                source=FakeDataSource(_make_clean_df(50)), storage=storage
            ).run(BUSINESS_DATE)
            ids.add(report.run_id)
        assert len(ids) == 5

    def test_duration_is_always_positive(self) -> None:
        for _ in range(3):
            storage = FakeDataStorage()
            report = ETLPipeline(
                source=FakeDataSource(_make_clean_df(100)), storage=storage
            ).run(BUSINESS_DATE)
            assert report.duration_seconds >= 0.0

    def test_deduplication_is_idempotent(self) -> None:
        """Running the pipeline on already-deduplicated data changes nothing."""
        df = _make_clean_df(200)
        s1 = FakeDataStorage()
        s2 = FakeDataStorage()
        ETLPipeline(source=FakeDataSource(df), storage=s1).run(BUSINESS_DATE)
        # Simulate re-running on same data (all ids already unique)
        ETLPipeline(source=FakeDataSource(df), storage=s2).run(BUSINESS_DATE)
        assert s1.total_records_written() == s2.total_records_written()
