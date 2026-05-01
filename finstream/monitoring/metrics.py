from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from prometheus_client import REGISTRY as DEFAULT_REGISTRY


class PipelineMetrics:
    """Prometheus metrics for the finstream ETL pipeline.

    All metrics accept an optional CollectorRegistry so unit tests can
    use an isolated registry and avoid duplicate-registration errors.
    """

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        reg = registry or DEFAULT_REGISTRY

        self._runs_total = Counter(
            "finstream_pipeline_runs_total",
            "Total pipeline runs by status",
            ["status"],
            registry=reg,
        )
        self._quality_score = Gauge(
            "finstream_quality_score",
            "Quality score of the last pipeline run (0–100)",
            registry=reg,
        )
        self._records_processed = Counter(
            "finstream_records_processed_total",
            "Total records processed across all runs",
            registry=reg,
        )
        self._chunk_duration = Histogram(
            "finstream_chunk_processing_seconds",
            "Time to process a single chunk",
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            registry=reg,
        )

    def record_run(self, status: str) -> None:
        """Increment the run counter for the given status label."""
        self._runs_total.labels(status=status).inc()

    def record_quality_score(self, score: float) -> None:
        """Update the quality score gauge."""
        self._quality_score.set(score)

    def record_records_processed(self, count: int) -> None:
        """Increment the total records counter by count."""
        self._records_processed.inc(count)

    def record_chunk_duration(self, seconds: float) -> None:
        """Observe a chunk processing time in the histogram."""
        self._chunk_duration.observe(seconds)

    def get_run_count(self, status: str) -> float:
        """Return the current value of the run counter for a given status."""
        return float(self._runs_total.labels(status=status)._value.get())

    def get_quality_score(self) -> float:
        """Return the current quality score gauge value."""
        return float(self._quality_score._value.get())

    def get_records_processed(self) -> float:
        """Return the total records processed counter value."""
        return float(self._records_processed._value.get())
