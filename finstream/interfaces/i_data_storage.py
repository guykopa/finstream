from abc import ABC, abstractmethod

import pandas as pd


class IDataStorage(ABC):
    """Contract for writing processed data in chunks."""

    @abstractmethod
    def write_chunk(self, df: pd.DataFrame, table: str) -> None:
        """Write a single DataFrame chunk to storage.

        Args:
            df: Processed DataFrame chunk to persist.
            table: Target table or collection name.
        """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the storage backend is reachable."""
