from typing import Iterator

import pandas as pd

from finstream.interfaces.i_data_storage import IDataStorage


class Loader:
    """Write a stream of DataFrame chunks to storage, chunk by chunk.

    Never holds more than one chunk in memory at a time.
    """

    def __init__(self, storage: IDataStorage, table: str = "transactions") -> None:
        self._storage = storage
        self._table = table

    def load(self, chunks: Iterator[pd.DataFrame]) -> int:
        """Consume a chunk iterator and write each chunk to storage.

        Args:
            chunks: Iterator of processed DataFrame chunks.

        Returns:
            Total number of records written.

        Raises:
            DataStorageError: if writing any chunk fails.
        """
        total = 0
        for chunk in chunks:
            self._storage.write_chunk(chunk, self._table)
            total += len(chunk)
        return total
