from datetime import date
from typing import Iterator

import pandas as pd

from finstream.domain.exceptions import DataSourceUnavailableError
from finstream.interfaces.i_data_source import IDataSource


class Extractor(IDataSource):
    """Select the first available data source from a priority-ordered list.

    Allows graceful fallback: try PostgreSQL first, then CSV, then REST API.
    """

    def __init__(self, sources: list[IDataSource]) -> None:
        if not sources:
            raise ValueError("At least one data source must be provided")
        self._sources = sources

    def _active_source(self) -> IDataSource:
        for source in self._sources:
            if source.is_available():
                return source
        raise DataSourceUnavailableError("all configured sources are unavailable")

    def read_chunks(
        self,
        business_date: date,
        chunk_size: int = 10_000,
    ) -> Iterator[pd.DataFrame]:
        """Delegate chunk reading to the first available source.

        Args:
            business_date: The business date to extract.
            chunk_size: Number of records per chunk.

        Yields:
            DataFrame chunks from the active source.

        Raises:
            DataSourceUnavailableError: if no source is reachable.
        """
        yield from self._active_source().read_chunks(business_date, chunk_size)

    def is_available(self) -> bool:
        """Return True if at least one source is reachable."""
        return any(source.is_available() for source in self._sources)
