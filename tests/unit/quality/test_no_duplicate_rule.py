import pandas as pd
import pytest

from finstream.quality.no_duplicate_rule import NoDuplicateRule


class TestNoDuplicateRule:
    """Unit tests for NoDuplicateRule."""

    def test_passes_on_valid_data(self, valid_transactions_df: pd.DataFrame) -> None:
        rule = NoDuplicateRule()
        result = rule.validate(valid_transactions_df)
        assert result.passed is True
        assert result.failed_count == 0

    def test_fails_on_duplicate_ids(self, df_with_duplicates: pd.DataFrame) -> None:
        rule = NoDuplicateRule()
        result = rule.validate(df_with_duplicates)
        assert result.passed is False
        assert result.failed_count >= 1

    def test_error_samples_contain_duplicate_ids(
        self, df_with_duplicates: pd.DataFrame
    ) -> None:
        rule = NoDuplicateRule()
        result = rule.validate(df_with_duplicates)
        assert len(result.error_samples) > 0

    def test_counts_only_extra_occurrences(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        df = pd.concat([valid_transactions_df, valid_transactions_df], ignore_index=True)
        rule = NoDuplicateRule()
        result = rule.validate(df)
        # 5 original + 5 duplicates → 5 extra occurrences flagged
        assert result.failed_count == 5

    def test_passes_on_empty_dataframe(self) -> None:
        rule = NoDuplicateRule()
        empty = pd.DataFrame(columns=["id"])
        result = rule.validate(empty)
        assert result.passed is True
        assert result.failed_count == 0

    def test_rule_name_is_not_empty(self) -> None:
        assert NoDuplicateRule().rule_name() != ""

    def test_result_contains_rule_name(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        rule = NoDuplicateRule()
        result = rule.validate(valid_transactions_df)
        assert result.rule_name == rule.rule_name()
