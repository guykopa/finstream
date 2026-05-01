import pytest

from finstream.monitoring.alerting import Alert, AlertingService, AlertSeverity


class TestAlertingService:
    """Unit tests for AlertingService."""

    def test_no_alert_when_quality_above_threshold(self) -> None:
        received: list[Alert] = []
        service = AlertingService(handlers=[received.append])
        service.check_quality(score=95.0, run_id="run-1", threshold=80.0)
        assert received == []

    def test_alert_raised_when_quality_below_threshold(self) -> None:
        received: list[Alert] = []
        service = AlertingService(handlers=[received.append])
        service.check_quality(score=60.0, run_id="run-1", threshold=80.0)
        assert len(received) == 1
        assert received[0].severity == AlertSeverity.WARNING

    def test_alert_is_critical_when_quality_very_low(self) -> None:
        received: list[Alert] = []
        service = AlertingService(handlers=[received.append])
        service.check_quality(score=20.0, run_id="run-1", threshold=80.0)
        assert received[0].severity == AlertSeverity.CRITICAL

    def test_pipeline_failure_sends_critical_alert(self) -> None:
        received: list[Alert] = []
        service = AlertingService(handlers=[received.append])
        service.notify_pipeline_failure(run_id="run-1", reason="DB down")
        assert len(received) == 1
        assert received[0].severity == AlertSeverity.CRITICAL

    def test_alert_contains_run_id(self) -> None:
        received: list[Alert] = []
        service = AlertingService(handlers=[received.append])
        service.check_quality(score=50.0, run_id="run-42", threshold=80.0)
        assert received[0].run_id == "run-42"

    def test_multiple_handlers_all_called(self) -> None:
        bucket_a: list[Alert] = []
        bucket_b: list[Alert] = []
        service = AlertingService(handlers=[bucket_a.append, bucket_b.append])
        service.notify_pipeline_failure(run_id="run-1", reason="timeout")
        assert len(bucket_a) == 1
        assert len(bucket_b) == 1

    def test_no_alert_on_exact_threshold(self) -> None:
        received: list[Alert] = []
        service = AlertingService(handlers=[received.append])
        service.check_quality(score=80.0, run_id="run-1", threshold=80.0)
        assert received == []
