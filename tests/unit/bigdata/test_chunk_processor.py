import pandas as pd

from finstream.bigdata.chunk_processor import ChunkProcessor


class TestChunkProcessor:
    """Unit tests for ChunkProcessor."""

    def test_splits_dataframe_into_chunks(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        # 5 rows, chunk_size=2 → 3 chunks (2, 2, 1)
        chunks = list(ChunkProcessor(chunk_size=2).process(valid_transactions_df))
        assert len(chunks) == 3

    def test_chunk_sizes_are_correct(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        chunks = list(ChunkProcessor(chunk_size=2).process(valid_transactions_df))
        assert len(chunks[0]) == 2
        assert len(chunks[1]) == 2
        assert len(chunks[2]) == 1  # remainder

    def test_all_rows_are_preserved(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        chunks = list(ChunkProcessor(chunk_size=2).process(valid_transactions_df))
        total = sum(len(c) for c in chunks)
        assert total == len(valid_transactions_df)

    def test_chunk_size_larger_than_df_returns_one_chunk(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        chunks = list(ChunkProcessor(chunk_size=10_000).process(valid_transactions_df))
        assert len(chunks) == 1
        assert len(chunks[0]) == len(valid_transactions_df)

    def test_large_dataframe_chunked_correctly(self, large_df: pd.DataFrame) -> None:
        chunk_size = 10_000
        chunks = list(ChunkProcessor(chunk_size=chunk_size).process(large_df))
        assert len(chunks) == 10  # 100_000 / 10_000
        assert all(len(c) == chunk_size for c in chunks)

    def test_empty_dataframe_yields_no_chunks(self) -> None:
        empty = pd.DataFrame(columns=["id", "amount"])
        chunks = list(ChunkProcessor(chunk_size=100).process(empty))
        assert chunks == []

    def test_chunks_are_independent_copies(
        self, valid_transactions_df: pd.DataFrame
    ) -> None:
        chunks = list(ChunkProcessor(chunk_size=3).process(valid_transactions_df))
        chunks[0].loc[chunks[0].index[0], "amount"] = 99999.0
        # original must be untouched
        assert valid_transactions_df.loc[0, "amount"] != 99999.0
