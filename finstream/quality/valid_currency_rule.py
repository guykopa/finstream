import pandas as pd

from finstream.domain.models.currency import Currency
from finstream.domain.models.quality_result import QualityResult
from finstream.interfaces.i_quality_rule import IQualityRule

_VALID_CURRENCIES = {c.value for c in Currency}


class ValidCurrencyRule(IQualityRule):
    """Quality rule: currency must be one of EUR, USD, GBP, CHF."""

    def rule_name(self) -> str:
        return "ValidCurrencyRule"

    def validate(self, df: pd.DataFrame) -> QualityResult:
        """Check that every currency value is in the supported Currency enum.

        Args:
            df: DataFrame chunk to validate.

        Returns:
            QualityResult with count of rows with unsupported currencies.
        """
        if df.empty or "currency" not in df.columns:
            return QualityResult(rule_name=self.rule_name(), passed=True, failed_count=0)

        failed_mask = ~df["currency"].isin(_VALID_CURRENCIES)
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
