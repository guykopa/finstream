import pytest

from finstream.domain.exceptions import QualityGateError
from finstream.domain.models.pipeline_report import QualityStatus
from finstream.quality.no_duplicate_rule import NoDuplicateRule
from finstream.quality.not_null_rule import NotNullRule
from finstream.quality.positive_amount_rule import PositiveAmountRule
from finstream.quality.quality_engine import QualityEngine
from finstream.quality.valid_currency_rule import ValidCurrencyRule
import pandas as pd


class TestQualityEngine:
    """Unit tests for QualityEngine."""

    def test_all_rules_pass_on_valid_data(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        engine = QualityEngine(rules=[
            NotNullRule(), PositiveAmountRule(), ValidCurrencyRule(),
        ])
        report = engine.run(valid_transactions_df)
        assert report.quality_score == 100.0
        assert report.status == QualityStatus.PASSED

    def test_quality_score_reflects_failed_rules(
        self, df_with_nulls: pd.DataFrame
    ) -> None:
        # threshold=0.0 disables the gate so we can inspect the returned score
        engine = QualityEngine(
            rules=[NotNullRule(), PositiveAmountRule()],
            quality_gate_threshold=0.0,
        )
        report = engine.run(df_with_nulls)
        assert report.quality_score == 50.0

    def test_raises_quality_gate_error_below_threshold(
        self, df_with_nulls: pd.DataFrame
    ) -> None:
        engine = QualityEngine(
            rules=[NotNullRule(), PositiveAmountRule(),
                   ValidCurrencyRule(), NoDuplicateRule()],
            quality_gate_threshold=80.0,
        )
        with pytest.raises(QualityGateError):
            engine.run(df_with_nulls)

    def test_empty_rules_list_returns_perfect_score(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        engine = QualityEngine(rules=[])
        report = engine.run(valid_transactions_df)
        assert report.quality_score == 100.0

    def test_status_is_warning_when_score_above_gate_but_not_perfect(
        self, df_with_nulls: pd.DataFrame
    ) -> None:
        engine = QualityEngine(
            rules=[NotNullRule(), PositiveAmountRule()],
            quality_gate_threshold=40.0,
        )
        report = engine.run(df_with_nulls)
        assert report.status == QualityStatus.WARNING

    def test_report_contains_one_result_per_rule(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        rules = [NotNullRule(), PositiveAmountRule(), ValidCurrencyRule()]
        engine = QualityEngine(rules=rules)
        report = engine.run(valid_transactions_df)
        assert len(report.results) == 3

    def test_no_gate_error_when_threshold_is_zero(
        self, df_with_nulls: pd.DataFrame
    ) -> None:
        engine = QualityEngine(
            rules=[NotNullRule()],
            quality_gate_threshold=0.0,
        )
        report = engine.run(df_with_nulls)
        assert report is not None
