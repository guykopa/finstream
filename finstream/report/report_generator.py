import dataclasses
import json

from finstream.domain.models.pipeline_report import PipelineReport
from finstream.interfaces.i_report_generator import IReportGenerator


class JSONReportGenerator(IReportGenerator):
    """Serialize a PipelineReport to a pretty-printed JSON string."""

    def generate(self, report: PipelineReport) -> str:
        """Convert a PipelineReport dataclass to a JSON string.

        Args:
            report: The completed pipeline report.

        Returns:
            Indented JSON string with all report fields.
            Dates and enums are serialized to their string representation.
        """
        return json.dumps(
            dataclasses.asdict(report),
            indent=2,
            default=str,
        )
