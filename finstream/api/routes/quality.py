from fastapi import APIRouter, Depends, HTTPException

from finstream.api.dependencies import get_quality_service, require_auth
from finstream.api.schemas import QualityReportResponse
from finstream.domain.exceptions import FinStreamError
from finstream.domain.services.quality_service import QualityService

router = APIRouter(prefix="/quality", tags=["quality"])


@router.get("/reports", response_model=list[str])
def list_reports(
    email: str = Depends(require_auth),
    quality_service: QualityService = Depends(get_quality_service),
) -> list[str]:
    """List all pipeline run IDs that have quality reports."""
    return quality_service.list_run_ids()


@router.get("/reports/{run_id}", response_model=list[QualityReportResponse])
def get_report(
    run_id: str,
    email: str = Depends(require_auth),
    quality_service: QualityService = Depends(get_quality_service),
) -> list[QualityReportResponse]:
    """Return quality results for a given pipeline run.

    Args:
        run_id: Pipeline run identifier.

    Raises:
        HTTPException 404: if no quality report exists for this run.
    """
    try:
        results = quality_service.get_results(run_id)
    except FinStreamError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return [
        QualityReportResponse(
            run_id=run_id,
            rule_name=r.rule_name,
            passed=r.passed,
            failed_count=r.failed_count,
            error_samples=r.error_samples,
            checked_at=r.checked_at,
        )
        for r in results
    ]
