import pandas as pd

from finstream.quality.date_range_rule import DateRangeRule


class TestDateRangeRule:
    """Unit tests for DateRangeRule."""

    def test_passes_on_valid_data(self, valid_transactions_df: pd.DataFrame) -> None:
        rule = DateRangeRule()
        result = rule.validate(valid_transactions_df)
        assert result.passed is True
        assert result.failed_count == 0

    def test_fails_on_future_dates(self, df_with_future_dates: pd.DataFrame) -> None:
        rule = DateRangeRule()
        result = rule.validate(df_with_future_dates)
        assert result.passed is False
        assert result.failed_count == 1

    def test_fails_on_dates_older_than_five_years(
        self, df_with_old_dates: pd.DataFrame
    ) -> None:
        rule = DateRangeRule()
        result = rule.validate(df_with_old_dates)
        assert result.passed is False
        assert result.failed_count == 1

    def test_error_samples_populated_on_failure(
        self, df_with_future_dates: pd.DataFrame
    ) -> None:
        rule = DateRangeRule()
        result = rule.validate(df_with_future_dates)
        assert len(result.error_samples) > 0

    def test_passes_on_empty_dataframe(self) -> None:
        rule = DateRangeRule()
        empty = pd.DataFrame(columns=["id", "date"])
        result = rule.validate(empty)
        assert result.passed is True
        assert result.failed_count == 0

    def test_rule_name_is_not_empty(self) -> None:
        assert DateRangeRule().rule_name() != ""

    def test_result_contains_rule_name(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        rule = DateRangeRule()
        result = rule.validate(valid_transactions_df)
        assert result.rule_name == rule.rule_name()
