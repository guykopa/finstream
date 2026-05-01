from datetime import date

import pandas as pd
import pytest

from tests.conftest import FakeDataSource, FakeDataStorage
from finstream.domain.exceptions import QualityGateError
from finstream.domain.models.pipeline_report import PipelineStatus
from finstream.domain.services.etl_service import ETLService
from finstream.quality.not_null_rule import NotNullRule
from finstream.quality.positive_amount_rule import PositiveAmountRule


BUSINESS_DATE = date(2024, 1, 15)


class TestETLService:
    """Unit tests for ETLService."""

    def test_run_returns_pipeline_report(
        self, valid_transactions_df: pd.DataFrame, fake_storage: FakeDataStorage
    ) -> None:
        source = FakeDataSource(valid_transactions_df)
        service = ETLService(source=source, storage=fake_storage)
        report = service.run(business_date=BUSINESS_DATE)
        assert report is not None
        assert report.run_id != ""

    def test_all_records_written_to_storage(
        self, valid_transactions_df: pd.DataFrame, fake_storage: FakeDataStorage
    ) -> None:
        source = FakeDataSource(valid_transactions_df)
        service = ETLService(source=source, storage=fake_storage)
        service.run(business_date=BUSINESS_DATE)
        assert fake_storage.total_records_written() == len(valid_transactions_df)

    def test_report_total_records_matches_source(
        self, valid_transactions_df: pd.DataFrame, fake_storage: FakeDataStorage
    ) -> None:
        source = FakeDataSource(valid_transactions_df)
        service = ETLService(source=source, storage=fake_storage)
        report = service.run(business_date=BUSINESS_DATE)
        assert report.total_records == len(valid_transactions_df)

    def test_report_status_is_completed_on_success(
        self, valid_transactions_df: pd.DataFrame, fake_storage: FakeDataStorage
    ) -> None:
        source = FakeDataSource(valid_transactions_df)
        service = ETLService(source=source, storage=fake_storage)
        report = service.run(business_date=BUSINESS_DATE)
        assert report.status == PipelineStatus.COMPLETED

    def test_report_duration_is_positive(
        self, valid_transactions_df: pd.DataFrame, fake_storage: FakeDataStorage
    ) -> None:
        source = FakeDataSource(valid_transactions_df)
        service = ETLService(source=source, storage=fake_storage)
        report = service.run(business_date=BUSINESS_DATE)
        assert report.duration_seconds >= 0.0

    def test_large_dataset_processed_in_multiple_chunks(
        self, large_df: pd.DataFrame, fake_storage: FakeDataStorage
    ) -> None:
        source = FakeDataSource(large_df)
        service = ETLService(source=source, storage=fake_storage, chunk_size=10_000)
        report = service.run(business_date=BUSINESS_DATE)
        assert report.chunk_count == 10
        assert fake_storage.total_records_written() == len(large_df)

    def test_raises_quality_gate_error_on_bad_data(
        self, df_with_nulls: pd.DataFrame, fake_storage: FakeDataStorage
    ) -> None:
        source = FakeDataSource(df_with_nulls)
        service = ETLService(
            source=source,
            storage=fake_storage,
            rules=[NotNullRule(), PositiveAmountRule()],
            quality_gate_threshold=80.0,
        )
        with pytest.raises(QualityGateError):
            service.run(business_date=BUSINESS_DATE)

    def test_quality_score_is_100_on_valid_data(
        self, valid_transactions_df: pd.DataFrame, fake_storage: FakeDataStorage
    ) -> None:
        source = FakeDataSource(valid_transactions_df)
        service = ETLService(
            source=source,
            storage=fake_storage,
            rules=[NotNullRule(), PositiveAmountRule()],
        )
        report = service.run(business_date=BUSINESS_DATE)
        assert report.quality_score == 100.0
