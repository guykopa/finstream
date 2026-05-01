import json
import logging

import pytest

from finstream.monitoring.logger import StructuredLogger


class TestStructuredLogger:
    """Unit tests for StructuredLogger — verifies JSON output format."""

    @pytest.fixture
    def logger_and_handler(self):
        """Return a StructuredLogger wired to a MemoryHandler for inspection."""
        import logging

        memory_handler = logging.handlers.MemoryHandler(capacity=100, flushLevel=100)
        logger = StructuredLogger(name="test", handlers=[memory_handler])
        return logger, memory_handler

    def test_info_produces_json_output(self, caplog) -> None:
        logger = StructuredLogger(name="test_info")
        with caplog.at_level(logging.INFO, logger="test_info"):
            logger.info("pipeline started", run_id="run-1")
        assert len(caplog.records) == 1

    def test_log_record_contains_message(self, caplog) -> None:
        logger = StructuredLogger(name="test_msg")
        with caplog.at_level(logging.INFO, logger="test_msg"):
            logger.info("hello world")
        assert "hello world" in caplog.records[0].getMessage()

    def test_extra_fields_attached_to_record(self, caplog) -> None:
        logger = StructuredLogger(name="test_extra")
        with caplog.at_level(logging.INFO, logger="test_extra"):
            logger.info("test", run_id="abc-123", chunk=5)
        record = caplog.records[0]
        assert getattr(record, "run_id", None) == "abc-123"
        assert getattr(record, "chunk", None) == 5

    def test_error_level_logged_correctly(self, caplog) -> None:
        logger = StructuredLogger(name="test_err")
        with caplog.at_level(logging.ERROR, logger="test_err"):
            logger.error("something failed", code=500)
        assert caplog.records[0].levelname == "ERROR"

    def test_warning_level_logged_correctly(self, caplog) -> None:
        logger = StructuredLogger(name="test_warn")
        with caplog.at_level(logging.WARNING, logger="test_warn"):
            logger.warning("quality below threshold", score=72.0)
        assert caplog.records[0].levelname == "WARNING"

    def test_json_formatter_produces_valid_json(self) -> None:
        from finstream.monitoring.logger import JSONFormatter
        import logging

        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test message", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "message" in parsed
        assert "level" in parsed
        assert "timestamp" in parsed
