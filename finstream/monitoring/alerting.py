from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable


class AlertSeverity(str, Enum):
    """Alert severity level."""

    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class Alert:
    """An alert produced by AlertingService.

    Attributes:
        severity: WARNING or CRITICAL.
        title: Short description of the alert condition.
        message: Detailed explanation.
        run_id: Pipeline run that triggered the alert.
        triggered_at: UTC timestamp of the alert.
    """

    severity: AlertSeverity
    title: str
    message: str
    run_id: str
    triggered_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


# A handler is any callable that accepts an Alert.
AlertHandler = Callable[[Alert], None]

# Score below this is CRITICAL, above (but below threshold) is WARNING.
_CRITICAL_SCORE_THRESHOLD = 50.0


class AlertingService:
    """Evaluate pipeline conditions and dispatch alerts to registered handlers.

    Handlers can be anything: in-memory lists (tests), email, Slack, PagerDuty.
    Add a new notification channel by passing a new handler — zero existing
    code modified.
    """

    def __init__(self, handlers: list[AlertHandler]) -> None:
        self._handlers = handlers

    def check_quality(
        self, score: float, run_id: str, threshold: float = 80.0
    ) -> None:
        """Send an alert if score falls below threshold.

        Args:
            score: Quality score (0–100) of the pipeline run.
            run_id: Identifier of the pipeline run.
            threshold: Minimum acceptable score before alerting.
        """
        if score >= threshold:
            return

        severity = (
            AlertSeverity.CRITICAL if score < _CRITICAL_SCORE_THRESHOLD
            else AlertSeverity.WARNING
        )
        alert = Alert(
            severity=severity,
            title="Quality gate below threshold",
            message=f"Run {run_id}: quality score {score:.1f}% < {threshold:.1f}%",
            run_id=run_id,
        )
        self._dispatch(alert)

    def notify_pipeline_failure(self, run_id: str, reason: str) -> None:
        """Send a CRITICAL alert when the pipeline fails.

        Args:
            run_id: Identifier of the failed pipeline run.
            reason: Human-readable failure reason.
        """
        alert = Alert(
            severity=AlertSeverity.CRITICAL,
            title="Pipeline run failed",
            message=f"Run {run_id} failed: {reason}",
            run_id=run_id,
        )
        self._dispatch(alert)

    def _dispatch(self, alert: Alert) -> None:
        for handler in self._handlers:
            handler(alert)
