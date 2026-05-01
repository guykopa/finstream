import pandas as pd
import pytest

from finstream.quality.not_null_rule import NotNullRule


class TestNotNullRule:
    """Unit tests for NotNullRule."""

    def test_passes_on_valid_data(self, valid_transactions_df: pd.DataFrame) -> None:
        rule = NotNullRule()
        result = rule.validate(valid_transactions_df)
        assert result.passed is True
        assert result.failed_count == 0

    def test_fails_when_amount_is_null(self, df_with_nulls: pd.DataFrame) -> None:
        rule = NotNullRule()
        result = rule.validate(df_with_nulls)
        assert result.passed is False
        assert result.failed_count >= 1

    def test_fails_when_currency_is_null(self, df_with_nulls: pd.DataFrame) -> None:
        rule = NotNullRule()
        result = rule.validate(df_with_nulls)
        assert result.passed is False

    def test_error_samples_are_populated_on_failure(
        self, df_with_nulls: pd.DataFrame
    ) -> None:
        rule = NotNullRule()
        result = rule.validate(df_with_nulls)
        assert len(result.error_samples) > 0

    def test_passes_on_empty_dataframe(self) -> None:
        rule = NotNullRule()
        empty = pd.DataFrame(columns=["id", "amount", "currency", "date"])
        result = rule.validate(empty)
        assert result.passed is True
        assert result.failed_count == 0

    def test_rule_name_is_not_empty(self) -> None:
        rule = NotNullRule()
        assert rule.rule_name() != ""

    def test_result_contains_rule_name(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        rule = NotNullRule()
        result = rule.validate(valid_transactions_df)
        assert result.rule_name == rule.rule_name()
