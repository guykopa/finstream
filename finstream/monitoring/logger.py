import json
import logging
import logging.handlers
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Format log records as single-line JSON for log aggregation systems."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level":     record.levelname,
            "logger":    record.name,
            "message":   record.getMessage(),
        }

        # Attach any extra fields passed via logger.info("msg", run_id="x")
        skip = logging.LogRecord.__dict__.keys() | {
            "message", "asctime", "args", "exc_info", "exc_text", "stack_info",
        }
        for key, value in record.__dict__.items():
            if key not in skip and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload)


class StructuredLogger:
    """Thin wrapper around Python's logging that attaches extra fields as JSON.

    Usage:
        logger = StructuredLogger("finstream.pipeline")
        logger.info("chunk processed", run_id="abc", chunk_index=3, records=10_000)
    """

    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        handlers: list[logging.Handler] | None = None,
    ) -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)

        if not self._logger.handlers:
            if handlers:
                for handler in handlers:
                    handler.setFormatter(JSONFormatter())
                    self._logger.addHandler(handler)
            else:
                handler = logging.StreamHandler()
                handler.setFormatter(JSONFormatter())
                self._logger.addHandler(handler)

    def _log(self, level: int, message: str, **fields: Any) -> None:
        self._logger.log(level, message, extra=fields)

    def info(self, message: str, **fields: Any) -> None:
        """Log at INFO level with optional structured fields."""
        self._log(logging.INFO, message, **fields)

    def warning(self, message: str, **fields: Any) -> None:
        """Log at WARNING level with optional structured fields."""
        self._log(logging.WARNING, message, **fields)

    def error(self, message: str, **fields: Any) -> None:
        """Log at ERROR level with optional structured fields."""
        self._log(logging.ERROR, message, **fields)

    def debug(self, message: str, **fields: Any) -> None:
        """Log at DEBUG level with optional structured fields."""
        self._log(logging.DEBUG, message, **fields)
