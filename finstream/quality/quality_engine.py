from dataclasses import dataclass

import pandas as pd

from finstream.domain.exceptions import QualityGateError
from finstream.domain.models.pipeline_report import QualityStatus
from finstream.domain.models.quality_result import QualityResult
from finstream.interfaces.i_quality_rule import IQualityRule


@dataclass
class QualityReport:
    """Aggregated result of all quality rules run on a single chunk.

    Attributes:
        results: Individual QualityResult for each rule.
        quality_score: Percentage of rules that passed (0–100).
        status: PASSED / WARNING / FAILED derived from score and threshold.
    """

    results: list[QualityResult]
    quality_score: float
    status: QualityStatus


class QualityEngine:
    """Orchestrates quality rules and computes the aggregate quality score.

    Receives a list of IQualityRule via constructor injection.
    Never applies rules itself — delegates entirely to each rule.
    """

    def __init__(
        self,
        rules: list[IQualityRule],
        quality_gate_threshold: float = 80.0,
    ) -> None:
        self._rules = rules
        self._threshold = quality_gate_threshold

    def run(self, df: pd.DataFrame) -> QualityReport:
        """Apply all rules to the DataFrame chunk and return a QualityReport.

        Args:
            df: DataFrame chunk to validate.

        Returns:
            QualityReport with individual results and aggregate score.

        Raises:
            QualityGateError: if quality_score < quality_gate_threshold.
        """
        if not self._rules:
            return QualityReport(
                results=[],
                quality_score=100.0,
                status=QualityStatus.PASSED,
            )

        results = [rule.validate(df) for rule in self._rules]
        passed_count = sum(1 for r in results if r.passed)
        score = passed_count / len(results) * 100.0
        status = self._compute_status(score)

        if score < self._threshold:
            raise QualityGateError(score=score, threshold=self._threshold)

        return QualityReport(results=results, quality_score=score, status=status)

    def _compute_status(self, score: float) -> QualityStatus:
        if score == 100.0:
            return QualityStatus.PASSED
        if score >= self._threshold:
            return QualityStatus.WARNING
        return QualityStatus.FAILED
