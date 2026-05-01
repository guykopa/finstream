from datetime import datetime, timezone

import pandas as pd

from finstream.domain.models.quality_result import QualityResult
from finstream.interfaces.i_quality_rule import IQualityRule

_MAX_YEARS_IN_PAST = 5


class DateRangeRule(IQualityRule):
    """Quality rule: date must not be in the future or older than 5 years."""

    def rule_name(self) -> str:
        return "DateRangeRule"

    def validate(self, df: pd.DataFrame) -> QualityResult:
        """Check that every transaction date is within the acceptable range.

        Args:
            df: DataFrame chunk to validate.

        Returns:
            QualityResult with count of out-of-range dates and sample ids.
        """
        if df.empty or "date" not in df.columns:
            return QualityResult(rule_name=self.rule_name(), passed=True, failed_count=0)

        now = pd.Timestamp.now(tz=None)
        oldest_allowed = now - pd.DateOffset(years=_MAX_YEARS_IN_PAST)

        dates = pd.to_datetime(df["date"]).dt.tz_localize(None)
        failed_mask = (dates > now) | (dates < oldest_allowed)
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
