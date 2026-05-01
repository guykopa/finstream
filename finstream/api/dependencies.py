"""FastAPI dependency providers — injected into routes via Depends()."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from finstream.api.security.jwt_handler import JWTError, JWTHandler
from finstream.api.security.rate_limiter import RateLimiter
from finstream.domain.services.quality_service import QualityService
from finstream.monitoring.alerting import AlertingService
from finstream.monitoring.logger import StructuredLogger
from finstream.monitoring.metrics import PipelineMetrics

_bearer = HTTPBearer()

# Singletons shared across requests
_jwt_handler = JWTHandler()
_rate_limiter = RateLimiter(max_requests=60, window_seconds=60)
_quality_service = QualityService()
_metrics = PipelineMetrics()
_logger = StructuredLogger("finstream.api")
_alerting = AlertingService(handlers=[
    lambda alert: _logger.warning(
        "alert triggered",
        severity=alert.severity.value,
        title=alert.title,
        run_id=alert.run_id,
    )
])


def get_jwt_handler() -> JWTHandler:
    return _jwt_handler


def get_rate_limiter() -> RateLimiter:
    return _rate_limiter


def get_quality_service() -> QualityService:
    return _quality_service


def get_metrics() -> PipelineMetrics:
    return _metrics


def get_logger() -> StructuredLogger:
    return _logger


def get_alerting() -> AlertingService:
    return _alerting


def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    handler: JWTHandler = Depends(get_jwt_handler),
) -> str:
    """Dependency that verifies the Bearer JWT and returns the email."""
    try:
        return handler.verify_token(credentials.credentials)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
