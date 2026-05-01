import pandas as pd

from finstream.domain.models.quality_result import QualityResult
from finstream.interfaces.i_quality_rule import IQualityRule


class NoDuplicateRule(IQualityRule):
    """Quality rule: transaction id must be unique within a chunk."""

    def rule_name(self) -> str:
        return "NoDuplicateRule"

    def validate(self, df: pd.DataFrame) -> QualityResult:
        """Check that no transaction id appears more than once.

        Args:
            df: DataFrame chunk to validate.

        Returns:
            QualityResult with count of duplicate rows (extra occurrences only).
        """
        if df.empty or "id" not in df.columns:
            return QualityResult(rule_name=self.rule_name(), passed=True, failed_count=0)

        duplicated_mask = df.duplicated(subset=["id"], keep="first")
        failed_rows = df[duplicated_mask]
        failed_count = len(failed_rows)

        error_samples: list[str] = []
        if failed_count > 0:
            error_samples = failed_rows["id"].astype(str).head(5).tolist()

        return QualityResult(
            rule_name=self.rule_name(),
            passed=failed_count == 0,
            failed_count=failed_count,
            error_samples=error_samples,
        )
