from datetime import date

import pandas as pd

from finstream.domain.models.pipeline_report import PipelineStatus
from finstream.pipeline.etl_pipeline import ETLPipeline
from tests.conftest import FakeDataSource, FakeDataStorage


def _valid_df() -> pd.DataFrame:
    return pd.DataFrame({
        "id":       ["tx-001", "tx-002"],
        "amount":   [100.0, 200.0],
        "currency": ["EUR", "USD"],
        "entity":   ["Apple", "LVMH"],
        "date":     ["2024-01-15", "2024-01-15"],
        "source":   ["csv", "csv"],
    })


class TestETLPipeline:
    def test_run_returns_pipeline_report(self) -> None:
        report = ETLPipeline(FakeDataSource(_valid_df()), FakeDataStorage()).run(date(2024, 1, 15))
        assert report is not None

    def test_run_status_is_completed(self) -> None:
        report = ETLPipeline(FakeDataSource(_valid_df()), FakeDataStorage()).run(date(2024, 1, 15))
        assert report.status == PipelineStatus.COMPLETED

    def test_records_written_to_storage(self) -> None:
        storage = FakeDataStorage()
        ETLPipeline(FakeDataSource(_valid_df()), storage).run(date(2024, 1, 15))
        assert storage.total_records_written() > 0

    def test_custom_exchange_rates_accepted(self) -> None:
        rates = {"EUR": 1.0, "USD": 0.85, "GBP": 1.15, "CHF": 1.05}
        report = ETLPipeline(
            FakeDataSource(_valid_df()), FakeDataStorage(), exchange_rates=rates
        ).run(date(2024, 1, 15))
        assert report.total_records > 0

    def test_empty_source_returns_zero_records(self) -> None:
        empty = pd.DataFrame(columns=["id", "amount", "currency", "entity", "date", "source"])
        report = ETLPipeline(FakeDataSource(empty), FakeDataStorage()).run(date(2024, 1, 15))
        assert report.total_records == 0
