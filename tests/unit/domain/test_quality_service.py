from datetime import datetime

import pytest

from finstream.domain.exceptions import FinStreamError
from finstream.domain.models.quality_result import QualityResult
from finstream.domain.services.quality_service import QualityService


def make_result(rule: str, passed: bool, failed: int = 0) -> QualityResult:
    return QualityResult(
        rule_name=rule,
        passed=passed,
        failed_count=failed,
        error_samples=[],
        checked_at=datetime(2024, 1, 15, 8, 0, 0),
    )


class TestQualityService:
    """Unit tests for QualityService."""

    def test_save_and_retrieve_results(self) -> None:
        service = QualityService()
        results = [make_result("NotNullRule", passed=True)]
        service.save_results("run-1", results)
        retrieved = service.get_results("run-1")
        assert len(retrieved) == 1
        assert retrieved[0].rule_name == "NotNullRule"

    def test_get_results_raises_for_unknown_run_id(self) -> None:
        service = QualityService()
        with pytest.raises(FinStreamError):
            service.get_results("unknown-run")

    def test_list_run_ids_returns_all_saved_runs(self) -> None:
        service = QualityService()
        service.save_results("run-1", [make_result("NotNullRule", passed=True)])
        service.save_results("run-2", [make_result("NotNullRule", passed=False)])
        run_ids = service.list_run_ids()
        assert "run-1" in run_ids
        assert "run-2" in run_ids

    def test_compute_score_all_passed_returns_100(self) -> None:
        service = QualityService()
        results = [
            make_result("NotNullRule", passed=True),
            make_result("PositiveAmountRule", passed=True),
        ]
        assert service.compute_score(results) == 100.0

    def test_compute_score_half_failed_returns_50(self) -> None:
        service = QualityService()
        results = [
            make_result("NotNullRule", passed=True),
            make_result("PositiveAmountRule", passed=False),
        ]
        assert service.compute_score(results) == 50.0

    def test_compute_score_empty_returns_100(self) -> None:
        service = QualityService()
        assert service.compute_score([]) == 100.0

    def test_save_overwrites_existing_run(self) -> None:
        service = QualityService()
        service.save_results("run-1", [make_result("NotNullRule", passed=True)])
        service.save_results("run-1", [make_result("NotNullRule", passed=False)])
        results = service.get_results("run-1")
        assert results[0].passed is False
