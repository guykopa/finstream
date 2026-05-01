import time
import uuid
from datetime import date, datetime

from finstream.bigdata.memory_optimizer import MemoryOptimizer
from finstream.domain.models.pipeline_report import PipelineReport, PipelineStatus
from finstream.interfaces.i_data_source import IDataSource
from finstream.interfaces.i_data_storage import IDataStorage
from finstream.interfaces.i_quality_rule import IQualityRule
from finstream.interfaces.i_transformer import ITransformer
from finstream.quality.quality_engine import QualityEngine


class ETLService:
    """Coordinate the full ETL pipeline: read → optimize → transform → validate → write.

    Receives all dependencies by constructor injection. Never instantiates
    adapters, transformers, or rules internally.
    """

    def __init__(
        self,
        source: IDataSource,
        storage: IDataStorage,
        transformers: list[ITransformer] | None = None,
        rules: list[IQualityRule] | None = None,
        chunk_size: int = 10_000,
        quality_gate_threshold: float = 80.0,
    ) -> None:
        self._source = source
        self._storage = storage
        self._transformers = transformers or []
        self._rules = rules or []
        self._chunk_size = chunk_size
        self._quality_gate_threshold = quality_gate_threshold

    def run(self, business_date: date) -> PipelineReport:
        """Execute the full pipeline for a given business date.

        Args:
            business_date: The business date to extract and process.

        Returns:
            PipelineReport summarising the run.

        Raises:
            QualityGateError: if the quality score falls below the threshold.
        """
        run_id = str(uuid.uuid4())
        started_at = datetime.utcnow()
        start_time = time.monotonic()

        optimizer = MemoryOptimizer()
        engine = QualityEngine(
            rules=self._rules,
            quality_gate_threshold=self._quality_gate_threshold,
        )

        total_records = 0
        chunk_count = 0
        last_quality_score = 100.0
        all_quality_results = []

        for chunk in self._source.read_chunks(business_date, self._chunk_size):
            chunk = optimizer.optimize(chunk)

            for transformer in self._transformers:
                chunk = transformer.transform(chunk)

            quality_report = engine.run(chunk)
            last_quality_score = quality_report.quality_score
            all_quality_results.extend(quality_report.results)

            self._storage.write_chunk(chunk, table="transactions")
            total_records += len(chunk)
            chunk_count += 1

        duration = time.monotonic() - start_time

        return PipelineReport(
            run_id=run_id,
            date=business_date,
            total_records=total_records,
            clean_records=total_records,
            quality_score=last_quality_score,
            duration_seconds=duration,
            chunk_count=chunk_count,
            memory_peak_mb=0.0,
            status=PipelineStatus.COMPLETED,
            started_at=started_at,
            quality_results=all_quality_results,
        )
