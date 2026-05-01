from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

import os

from sqlalchemy import create_engine

from finstream.api.dependencies import (
    get_alerting,
    get_logger,
    get_metrics,
    get_quality_service,
    require_auth,
)
from finstream.api.schemas import PipelineRunRequest, PipelineRunResponse
from finstream.domain.exceptions import (
    DataSourceUnavailableError,
    DataStorageError,
    QualityGateError,
)
from finstream.domain.services.quality_service import QualityService
from finstream.interfaces.i_data_source import IDataSource
from finstream.load.postgresql_storage import PostgreSQLStorage
from finstream.monitoring.alerting import AlertingService
from finstream.monitoring.logger import StructuredLogger
from finstream.monitoring.metrics import PipelineMetrics
from finstream.pipeline.etl_pipeline import ETLPipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

# In-memory store for run statuses (replace with DB in production)
_run_store: dict[str, dict[str, Any]] = {}


def _make_storage() -> PostgreSQLStorage:
    """Create a fresh PostgreSQL storage instance per request."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return PostgreSQLStorage(create_engine(database_url))


def _build_pipeline(request: PipelineRunRequest) -> ETLPipeline:
    """Build an ETLPipeline wired to the requested source and storage."""
    source: IDataSource
    if request.source == "csv":
        if not request.file_path:
            raise ValueError("file_path is required when source=csv")
        from finstream.extract.csv_source import CSVSource
        source = CSVSource(request.file_path)
    elif request.source == "live":
        from finstream.extract.yahoo_finance_api_source import YahooFinanceAPISource
        source = YahooFinanceAPISource()
    else:
        import pandas as pd
        from finstream.extract.fake_source import FakeDataSource
        sample = pd.DataFrame({
            "id":       [f"tx-{i:05d}" for i in range(50)],
            "amount":   [float(100 + i) for i in range(50)],
            "currency": ["EUR"] * 50,
            "entity":   [f"E{i % 5:03d}" for i in range(50)],
            "date":     [str(request.business_date)] * 50,
            "source":   ["api"] * 50,
        })
        source = FakeDataSource(sample)

    return ETLPipeline(
        source=source,
        storage=_make_storage(),
        quality_gate_threshold=request.quality_gate_threshold,
        chunk_size=request.chunk_size,
    )


@router.post("/run", response_model=PipelineRunResponse, status_code=status.HTTP_202_ACCEPTED)
def run_pipeline(
    body: PipelineRunRequest,
    email: str = Depends(require_auth),
    metrics: PipelineMetrics = Depends(get_metrics),
    logger: StructuredLogger = Depends(get_logger),
    alerting: AlertingService = Depends(get_alerting),
    quality_service: QualityService = Depends(get_quality_service),
) -> PipelineRunResponse:
    """Trigger the ETL pipeline for a given business date.

    Args:
        body: Pipeline run parameters.
        email: Authenticated user email (from JWT).

    Returns:
        PipelineRunResponse with run statistics.

    Raises:
        HTTPException 422: if quality gate fails.
        HTTPException 503: if data source is unavailable.
    """
    logger.info("pipeline run requested", user=email, date=str(body.business_date))

    try:
        pipeline = _build_pipeline(body)
        report = pipeline.run(body.business_date)
    except QualityGateError as exc:
        alerting.check_quality(exc.score, run_id="unknown", threshold=exc.threshold)
        metrics.record_run(status="FAILED")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except DataSourceUnavailableError as exc:
        metrics.record_run(status="FAILED")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except DataStorageError as exc:
        metrics.record_run(status="FAILED")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    metrics.record_run(status="COMPLETED")
    metrics.record_records_processed(report.total_records)
    metrics.record_quality_score(report.quality_score)
    _run_store[report.run_id] = {"status": "COMPLETED", "report": report}
    quality_service.save_results(report.run_id, report.quality_results)

    logger.info(
        "pipeline run completed",
        run_id=report.run_id,
        quality_score=report.quality_score,
        total_records=report.total_records,
    )

    return PipelineRunResponse(
        run_id=report.run_id,
        status=report.status.value,
        total_records=report.total_records,
        clean_records=report.clean_records,
        quality_score=report.quality_score,
        duration_seconds=report.duration_seconds,
        chunk_count=report.chunk_count,
        started_at=report.started_at,
    )


@router.get("/status/{run_id}", response_model=PipelineRunResponse)
def get_pipeline_status(
    run_id: str,
    email: str = Depends(require_auth),
) -> PipelineRunResponse:
    """Return the status and report for a completed pipeline run.

    Args:
        run_id: Pipeline run identifier returned by POST /pipeline/run.

    Raises:
        HTTPException 404: if the run_id is not found.
    """
    entry = _run_store.get(run_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    report = entry["report"]
    return PipelineRunResponse(
        run_id=report.run_id,
        status=report.status.value,
        total_records=report.total_records,
        clean_records=report.clean_records,
        quality_score=report.quality_score,
        duration_seconds=report.duration_seconds,
        chunk_count=report.chunk_count,
        started_at=report.started_at,
    )
