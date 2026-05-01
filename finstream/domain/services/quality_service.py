from finstream.domain.exceptions import FinStreamError
from finstream.domain.models.quality_result import QualityResult


class QualityReportNotFoundError(FinStreamError):
    """Raised when no quality results exist for the requested run_id."""

    def __init__(self, run_id: str) -> None:
        super().__init__(f"No quality results found for run '{run_id}'")


class QualityService:
    """Store and retrieve quality results for each pipeline run.

    Uses an in-memory dict in unit tests.
    In production, replace with a PostgreSQL-backed implementation
    behind the same interface.
    """

    def __init__(self) -> None:
        self._store: dict[str, list[QualityResult]] = {}

    def save_results(self, run_id: str, results: list[QualityResult]) -> None:
        """Persist quality results for a pipeline run.

        Args:
            run_id: Unique identifier of the pipeline run.
            results: List of QualityResult produced by the QualityEngine.
        """
        self._store[run_id] = results

    def get_results(self, run_id: str) -> list[QualityResult]:
        """Retrieve quality results for a given run.

        Args:
            run_id: Unique identifier of the pipeline run.

        Returns:
            List of QualityResult for that run.

        Raises:
            QualityReportNotFoundError: if no results exist for this run_id.
        """
        if run_id not in self._store:
            raise QualityReportNotFoundError(run_id)
        return self._store[run_id]

    def list_run_ids(self) -> list[str]:
        """Return all run IDs that have saved quality results."""
        return list(self._store.keys())

    def compute_score(self, results: list[QualityResult]) -> float:
        """Calculate the quality score as a percentage of passed rules.

        Args:
            results: List of QualityResult to score.

        Returns:
            Score between 0.0 and 100.0. Returns 100.0 for an empty list.
        """
        if not results:
            return 100.0
        passed = sum(1 for r in results if r.passed)
        return passed / len(results) * 100.0
