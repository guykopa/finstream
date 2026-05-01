import pandas as pd

from finstream.quality.valid_currency_rule import ValidCurrencyRule


class TestValidCurrencyRule:
    """Unit tests for ValidCurrencyRule."""

    def test_passes_on_valid_data(self, valid_transactions_df: pd.DataFrame) -> None:
        rule = ValidCurrencyRule()
        result = rule.validate(valid_transactions_df)
        assert result.passed is True
        assert result.failed_count == 0

    def test_fails_on_invalid_currencies(
        self, df_with_invalid_currencies: pd.DataFrame
    ) -> None:
        rule = ValidCurrencyRule()
        result = rule.validate(df_with_invalid_currencies)
        assert result.passed is False
        assert result.failed_count == 2

    def test_error_samples_contain_bad_currencies(
        self, df_with_invalid_currencies: pd.DataFrame
    ) -> None:
        rule = ValidCurrencyRule()
        result = rule.validate(df_with_invalid_currencies)
        assert len(result.error_samples) > 0

    def test_fails_on_lowercase_currency(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        df = valid_transactions_df.copy()
        df.loc[0, "currency"] = "eur"
        rule = ValidCurrencyRule()
        result = rule.validate(df)
        assert result.passed is False
        assert result.failed_count == 1

    def test_passes_on_empty_dataframe(self) -> None:
        rule = ValidCurrencyRule()
        empty = pd.DataFrame(columns=["id", "currency"])
        result = rule.validate(empty)
        assert result.passed is True
        assert result.failed_count == 0

    def test_rule_name_is_not_empty(self) -> None:
        assert ValidCurrencyRule().rule_name() != ""

    def test_result_contains_rule_name(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        rule = ValidCurrencyRule()
        result = rule.validate(valid_transactions_df)
        assert result.rule_name == rule.rule_name()
