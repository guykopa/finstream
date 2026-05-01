from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from finstream.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """System health check — always public, no JWT required.

    Returns:
        HealthResponse with overall status and per-component checks.
    """
    return HealthResponse(
        status="ok",
        checks={
            "api": "ok",
            "pipeline": "ok",
        },
    )


@router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    """Readiness probe for Kubernetes / load balancer.

    Returns HTTP 200 when the app is ready to serve traffic.
    """
    return HealthResponse(status="ready", checks={"api": "ready"})


@router.get("/metrics", response_class=PlainTextResponse)
def metrics() -> PlainTextResponse:
    """Expose Prometheus metrics in text format for scraping.

    This endpoint is scraped by Prometheus every 15 seconds.
    """
    return PlainTextResponse(
        content=generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )
