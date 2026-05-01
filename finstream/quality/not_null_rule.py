import pandas as pd

from finstream.domain.models.quality_result import QualityResult
from finstream.interfaces.i_quality_rule import IQualityRule

_REQUIRED_FIELDS = ["id", "amount", "currency", "date"]


class NotNullRule(IQualityRule):
    """Quality rule: required fields must not contain null values."""

    def rule_name(self) -> str:
        return "NotNullRule"

    def validate(self, df: pd.DataFrame) -> QualityResult:
        """Check that id, amount, currency and date are never null.

        Args:
            df: DataFrame chunk to validate.

        Returns:
            QualityResult with the count of rows containing at least one null
            in a required field, and up to 5 sample row ids.
        """
        existing_fields = [f for f in _REQUIRED_FIELDS if f in df.columns]
        null_mask = df[existing_fields].isnull().any(axis=1)
        failed_rows = df[null_mask]
        failed_count = len(failed_rows)

        error_samples: list[str] = []
        if failed_count > 0 and "id" in df.columns:
            error_samples = failed_rows["id"].astype(str).head(5).tolist()

        return QualityResult(
            rule_name=self.rule_name(),
            passed=failed_count == 0,
            failed_count=failed_count,
            error_samples=error_samples,
        )
