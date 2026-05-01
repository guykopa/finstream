from abc import ABC, abstractmethod

from finstream.domain.models.pipeline_report import PipelineReport


class IReportGenerator(ABC):
    """Contract for generating pipeline reports in various formats."""

    @abstractmethod
    def generate(self, report: PipelineReport) -> str:
        """Serialize a PipelineReport to a string (JSON, HTML, etc.).

        Args:
            report: The completed pipeline report to serialize.

        Returns:
            String representation of the report.
        """
