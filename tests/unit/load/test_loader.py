from typing import Iterator

import pandas as pd

from finstream.load.loader import Loader
from tests.conftest import FakeDataStorage


class TestLoader:
    def test_returns_total_record_count(self) -> None:
        storage = FakeDataStorage()
        loader = Loader(storage)
        df1 = pd.DataFrame({"id": ["tx-1", "tx-2"]})
        df2 = pd.DataFrame({"id": ["tx-3"]})

        def chunks() -> Iterator[pd.DataFrame]:
            yield df1
            yield df2

        assert loader.load(chunks()) == 3

    def test_writes_each_chunk_to_storage(self) -> None:
        storage = FakeDataStorage()
        loader = Loader(storage)

        def chunks() -> Iterator[pd.DataFrame]:
            yield pd.DataFrame({"id": ["tx-1", "tx-2"]})

        loader.load(chunks())
        assert len(storage.written_chunks) == 1

    def test_empty_iterator_returns_zero(self) -> None:
        storage = FakeDataStorage()
        loader = Loader(storage)
        assert loader.load(iter([])) == 0

    def test_multiple_chunks_all_written(self) -> None:
        storage = FakeDataStorage()
        loader = Loader(storage)

        def chunks() -> Iterator[pd.DataFrame]:
            for i in range(5):
                yield pd.DataFrame({"id": [f"tx-{i}"]})

        loader.load(chunks())
        assert len(storage.written_chunks) == 5

    def test_custom_table_name_passed_to_storage(self) -> None:
        storage = FakeDataStorage()
        written_tables: list[str] = []
        original = storage.write_chunk

        def capturing(df: pd.DataFrame, table: str) -> None:
            written_tables.append(table)
            original(df, table)

        storage.write_chunk = capturing  # type: ignore[method-assign]
        Loader(storage, table="positions").load(
            iter([pd.DataFrame({"id": ["tx-1"]})])
        )
        assert written_tables == ["positions"]
