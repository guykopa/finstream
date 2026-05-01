from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class QualityResult:
    """Result of a single quality rule applied to a DataFrame chunk.

    Attributes:
        rule_name: Name of the rule that produced this result.
        passed: True if all records passed the rule.
        failed_count: Number of records that failed the rule.
        error_samples: Up to 5 sample values that triggered failures.
        checked_at: UTC timestamp when the rule was evaluated.
    """

    rule_name: str
    passed: bool
    failed_count: int
    error_samples: list[str] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.utcnow)
