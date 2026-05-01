from datetime import date

from finstream.domain.models.pipeline_report import PipelineReport
from finstream.domain.services.etl_service import ETLService
from finstream.interfaces.i_data_source import IDataSource
from finstream.interfaces.i_data_storage import IDataStorage
from finstream.quality.date_range_rule import DateRangeRule
from finstream.quality.no_duplicate_rule import NoDuplicateRule
from finstream.quality.not_null_rule import NotNullRule
from finstream.quality.positive_amount_rule import PositiveAmountRule
from finstream.quality.valid_currency_rule import ValidCurrencyRule
from finstream.transform.currency_normalizer import CurrencyNormalizer
from finstream.transform.data_cleaner import DataCleaner
from finstream.transform.date_standardizer import DateStandardizer
from finstream.transform.deduplicator import Deduplicator

# Static fallback rates — replace with a live rate service in production.
_DEFAULT_EXCHANGE_RATES: dict[str, float] = {
    "EUR": 1.0,
    "USD": 0.92,
    "GBP": 1.17,
    "CHF": 1.06,
}


class ETLPipeline:
    """Top-level pipeline orchestrator.

    Wires source, storage, transformers and quality rules together,
    then delegates execution to ETLService.

    Args:
        source: Data source to extract transactions from.
        storage: Data storage to write clean records to.
        exchange_rates: Currency-to-EUR conversion rates.
            Defaults to static rates if not provided.
        quality_gate_threshold: Minimum quality score (0–100) before the
            pipeline aborts. Defaults to 80.0.
        chunk_size: Number of records per processing chunk. Defaults to 10_000.
    """

    def __init__(
        self,
        source: IDataSource,
        storage: IDataStorage,
        exchange_rates: dict[str, float] | None = None,
        quality_gate_threshold: float = 80.0,
        chunk_size: int = 10_000,
    ) -> None:
        rates = exchange_rates or _DEFAULT_EXCHANGE_RATES

        transformers = [
            DataCleaner(),
            CurrencyNormalizer(rates=rates),
            Deduplicator(),
            DateStandardizer(),
        ]

        rules = [
            NotNullRule(),
            PositiveAmountRule(),
            ValidCurrencyRule(),
            NoDuplicateRule(),
            DateRangeRule(),
        ]

        self._service = ETLService(
            source=source,
            storage=storage,
            transformers=transformers,
            rules=rules,
            chunk_size=chunk_size,
            quality_gate_threshold=quality_gate_threshold,
        )

    def run(self, business_date: date) -> PipelineReport:
        """Execute the full ETL pipeline for a given business date.

        Args:
            business_date: The business date to extract and process.

        Returns:
            PipelineReport with run statistics and quality score.

        Raises:
            QualityGateError: if quality_score < quality_gate_threshold.
            DataSourceUnavailableError: if the source cannot be reached.
        """
        return self._service.run(business_date)
