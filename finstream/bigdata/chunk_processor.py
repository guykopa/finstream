from typing import Iterator

import pandas as pd


class ChunkProcessor:
    """Split a DataFrame into fixed-size chunks for memory-safe processing.

    Yields independent copies so each chunk can be modified without
    affecting the source DataFrame or other chunks.
    """

    def __init__(self, chunk_size: int = 10_000) -> None:
        self._chunk_size = chunk_size

    def process(self, df: pd.DataFrame) -> Iterator[pd.DataFrame]:
        """Yield successive chunks from df.

        Args:
            df: Source DataFrame to split.

        Yields:
            DataFrame slices of at most chunk_size rows.
        """
        if df.empty:
            return

        for start in range(0, len(df), self._chunk_size):
            yield df.iloc[start : start + self._chunk_size].copy()
