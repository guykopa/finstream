import pandas as pd
import pytest

from finstream.quality.positive_amount_rule import PositiveAmountRule


class TestPositiveAmountRule:
    """Unit tests for PositiveAmountRule."""

    def test_passes_on_valid_data(self, valid_transactions_df: pd.DataFrame) -> None:
        rule = PositiveAmountRule()
        result = rule.validate(valid_transactions_df)
        assert result.passed is True
        assert result.failed_count == 0

    def test_fails_on_negative_amounts(
        self, df_with_negative_amounts: pd.DataFrame
    ) -> None:
        rule = PositiveAmountRule()
        result = rule.validate(df_with_negative_amounts)
        assert result.passed is False
        assert result.failed_count == 2

    def test_fails_on_zero_amount(self, valid_transactions_df: pd.DataFrame) -> None:
        df = valid_transactions_df.copy()
        df.loc[0, "amount"] = 0.0
        rule = PositiveAmountRule()
        result = rule.validate(df)
        assert result.passed is False
        assert result.failed_count == 1

    def test_error_samples_contain_bad_amounts(
        self, df_with_negative_amounts: pd.DataFrame
    ) -> None:
        rule = PositiveAmountRule()
        result = rule.validate(df_with_negative_amounts)
        assert len(result.error_samples) > 0

    def test_passes_on_empty_dataframe(self) -> None:
        rule = PositiveAmountRule()
        empty = pd.DataFrame(columns=["id", "amount"])
        result = rule.validate(empty)
        assert result.passed is True
        assert result.failed_count == 0

    def test_rule_name_is_not_empty(self) -> None:
        assert PositiveAmountRule().rule_name() != ""

    def test_result_contains_rule_name(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        rule = PositiveAmountRule()
        result = rule.validate(valid_transactions_df)
        assert result.rule_name == rule.rule_name()
