import pytest
from prometheus_client import CollectorRegistry

from finstream.monitoring.metrics import PipelineMetrics


class TestPipelineMetrics:
    """Unit tests for PipelineMetrics — each test gets an isolated registry."""

    @pytest.fixture
    def metrics(self) -> PipelineMetrics:
        return PipelineMetrics(registry=CollectorRegistry())

    def test_record_run_increments_completed_counter(
        self, metrics: PipelineMetrics
    ) -> None:
        metrics.record_run(status="COMPLETED")
        assert metrics.get_run_count(status="COMPLETED") == 1

    def test_record_run_increments_failed_counter(
        self, metrics: PipelineMetrics
    ) -> None:
        metrics.record_run(status="FAILED")
        assert metrics.get_run_count(status="FAILED") == 1

    def test_multiple_runs_accumulate(self, metrics: PipelineMetrics) -> None:
        metrics.record_run(status="COMPLETED")
        metrics.record_run(status="COMPLETED")
        metrics.record_run(status="FAILED")
        assert metrics.get_run_count(status="COMPLETED") == 2
        assert metrics.get_run_count(status="FAILED") == 1

    def test_record_quality_score_sets_gauge(
        self, metrics: PipelineMetrics
    ) -> None:
        metrics.record_quality_score(score=87.5)
        assert metrics.get_quality_score() == pytest.approx(87.5)

    def test_record_records_processed_increments_counter(
        self, metrics: PipelineMetrics
    ) -> None:
        metrics.record_records_processed(count=10_000)
        assert metrics.get_records_processed() == 10_000

    def test_record_chunk_duration(self, metrics: PipelineMetrics) -> None:
        metrics.record_chunk_duration(seconds=0.42)
        # Just verify no exception is raised — histogram internals are opaque
