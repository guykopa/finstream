from datetime import date
from pathlib import Path
from typing import Iterator

import pandas as pd

from finstream.domain.exceptions import DataSourceUnavailableError
from finstream.interfaces.i_data_source import IDataSource

_REQUIRED_COLUMNS = ["id", "amount", "currency", "entity", "date", "source"]


class CSVSource(IDataSource):
    """Read financial transactions from a CSV file in chunks.

    The CSV must contain columns: id, amount, currency, entity, date, source.
    """

    def __init__(self, file_path: str | Path) -> None:
        self._path = Path(file_path)

    def read_chunks(
        self,
        business_date: date,
        chunk_size: int = 10_000,
    ) -> Iterator[pd.DataFrame]:
        """Stream transactions for a given business date from a CSV file.

        Args:
            business_date: The date to filter transactions on.
            chunk_size: Number of rows per chunk before filtering.

        Yields:
            DataFrame chunks filtered to business_date.

        Raises:
            DataSourceUnavailableError: if the file does not exist.
        """
        if not self._path.exists():
            raise DataSourceUnavailableError(str(self._path))

        for chunk in pd.read_csv(
            self._path,
            chunksize=chunk_size,
            parse_dates=["date"],
        ):
            filtered = chunk[
                pd.to_datetime(chunk["date"]).dt.date == business_date
            ]
            if not filtered.empty:
                yield filtered.reset_index(drop=True)

    def is_available(self) -> bool:
        """Return True if the CSV file exists and is readable."""
        return self._path.exists() and self._path.is_file()
