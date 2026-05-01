class FinStreamError(Exception):
    """Base exception for all finstream errors."""


class QualityGateError(FinStreamError):
    """Raised when the quality score falls below the configured threshold."""

    def __init__(self, score: float, threshold: float) -> None:
        self.score = score
        self.threshold = threshold
        super().__init__(
            f"Quality gate failed: score {score:.1f}% is below threshold {threshold:.1f}%"
        )


class TransformationError(FinStreamError):
    """Raised when a transformer fails to process a DataFrame chunk."""

    def __init__(self, transformer: str, reason: str) -> None:
        self.transformer = transformer
        super().__init__(f"Transformation '{transformer}' failed: {reason}")


class DataSourceUnavailableError(FinStreamError):
    """Raised when a data source cannot be reached."""

    def __init__(self, source: str) -> None:
        self.source = source
        super().__init__(f"Data source '{source}' is unavailable")


class DataStorageError(FinStreamError):
    """Raised when writing a chunk to storage fails."""

    def __init__(self, table: str, reason: str) -> None:
        self.table = table
        super().__init__(f"Failed to write to '{table}': {reason}")


class PipelineError(FinStreamError):
    """Raised when the ETL pipeline encounters an unrecoverable error."""
