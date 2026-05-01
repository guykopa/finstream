import pandas as pd

from finstream.domain.models.quality_result import QualityResult
from finstream.interfaces.i_quality_rule import IQualityRule


class PositiveAmountRule(IQualityRule):
    """Quality rule: amount must be strictly greater than zero."""

    def rule_name(self) -> str:
        return "PositiveAmountRule"

    def validate(self, df: pd.DataFrame) -> QualityResult:
        """Check that every amount is strictly positive.

        Args:
            df: DataFrame chunk to validate.

        Returns:
            QualityResult with count of non-positive rows and sample ids.
        """
        if df.empty or "amount" not in df.columns:
            return QualityResult(rule_name=self.rule_name(), passed=True, failed_count=0)

        failed_mask = df["amount"] <= 0
        failed_rows = df[failed_mask]
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
