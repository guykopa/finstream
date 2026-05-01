import json

import pytest

from finstream.report.report_generator import JSONReportGenerator


class TestJSONReportGenerator:
    """Unit tests for JSONReportGenerator."""

    def test_generate_returns_valid_json(self, sample_pipeline_report) -> None:
        output = JSONReportGenerator().generate(sample_pipeline_report)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_output_contains_run_id(self, sample_pipeline_report) -> None:
        output = JSONReportGenerator().generate(sample_pipeline_report)
        assert sample_pipeline_report.run_id in output

    def test_output_contains_quality_score(self, sample_pipeline_report) -> None:
        output = JSONReportGenerator().generate(sample_pipeline_report)
        parsed = json.loads(output)
        assert parsed["quality_score"] == sample_pipeline_report.quality_score

    def test_output_contains_total_records(self, sample_pipeline_report) -> None:
        output = JSONReportGenerator().generate(sample_pipeline_report)
        parsed = json.loads(output)
        assert parsed["total_records"] == sample_pipeline_report.total_records

    def test_output_contains_status(self, sample_pipeline_report) -> None:
        output = JSONReportGenerator().generate(sample_pipeline_report)
        parsed = json.loads(output)
        assert parsed["status"] == sample_pipeline_report.status.value

    def test_output_is_pretty_printed(self, sample_pipeline_report) -> None:
        output = JSONReportGenerator().generate(sample_pipeline_report)
        assert "\n" in output
