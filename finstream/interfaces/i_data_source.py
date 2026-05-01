from abc import ABC, abstractmethod
from datetime import date
from typing import Iterator

import pandas as pd


class IDataSource(ABC):
    """Contract for reading financial data in chunks."""

    @abstractmethod
    def read_chunks(
        self,
        business_date: date,
        chunk_size: int = 10_000,
    ) -> Iterator[pd.DataFrame]:
        """Read financial transactions in chunks.

        Args:
            business_date: The business date to extract.
            chunk_size: Number of records per chunk.

        Yields:
            DataFrame chunks with columns:
            id, amount, currency, entity, date, source
        """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the data source is reachable."""
