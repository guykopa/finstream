"""In-memory data source for demo and development use."""
from datetime import date
from typing import Iterator

import pandas as pd

from finstream.interfaces.i_data_source import IDataSource


class FakeDataSource(IDataSource):
    """Data source backed by an in-memory DataFrame."""

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df

    def read_chunks(self, business_date: date, chunk_size: int = 10_000) -> Iterator[pd.DataFrame]:
        for start in range(0, len(self._df), chunk_size):
            yield self._df.iloc[start : start + chunk_size].copy()

    def is_available(self) -> bool:
        return True
