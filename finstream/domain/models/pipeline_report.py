from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from finstream.domain.models.quality_result import QualityResult


class QualityStatus(str, Enum):
    """Overall quality assessment of a pipeline run."""

    PASSED = "PASSED"
    WARNING = "WARNING"
    FAILED = "FAILED"


class PipelineStatus(str, Enum):
    """Execution status of a pipeline run."""

    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class PipelineReport:
    """Summary report produced at the end of a pipeline run.

    Attributes:
        run_id: Unique identifier for this pipeline execution.
        date: Business date that was processed.
        total_records: Total records read from the source.
        clean_records: Records that passed all quality rules.
        quality_score: Percentage of rules passed (0–100).
        duration_seconds: Wall-clock time of the full pipeline run.
        chunk_count: Number of chunks processed.
        memory_peak_mb: Peak RSS memory during the run.
        status: Final pipeline execution status.
        started_at: UTC timestamp when the pipeline started.
    """

    run_id: str
    date: date
    total_records: int
    clean_records: int
    quality_score: float
    duration_seconds: float
    chunk_count: int
    memory_peak_mb: float
    status: PipelineStatus
    started_at: datetime
    quality_results: list["QualityResult"] = field(default_factory=list, compare=False, hash=False)
