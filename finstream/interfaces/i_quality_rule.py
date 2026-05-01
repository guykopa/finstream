from abc import ABC, abstractmethod

import pandas as pd

from finstream.domain.models.quality_result import QualityResult


class IQualityRule(ABC):
    """Contract for a single stateless data quality rule."""

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> QualityResult:
        """Validate a DataFrame chunk against this rule.

        Args:
            df: DataFrame chunk to validate.

        Returns:
            QualityResult with pass/fail status and error samples.
        """

    @abstractmethod
    def rule_name(self) -> str:
        """Return the name of this rule for reporting."""
