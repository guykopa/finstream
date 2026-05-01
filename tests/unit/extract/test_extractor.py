from datetime import date
from typing import Iterator

import pandas as pd
import pytest

from finstream.domain.exceptions import DataSourceUnavailableError
from finstream.extract.extractor import Extractor
from finstream.interfaces.i_data_source import IDataSource


class _Available(IDataSource):
    def __init__(self, rows: list[str]) -> None:
        self._rows = rows

    def read_chunks(self, business_date: date, chunk_size: int = 10_000) -> Iterator[pd.DataFrame]:
        yield pd.DataFrame({"id": self._rows})

    def is_available(self) -> bool:
        return True


class _Unavailable(IDataSource):
    def read_chunks(self, business_date: date, chunk_size: int = 10_000) -> Iterator[pd.DataFrame]:
        return iter([])

    def is_available(self) -> bool:
        return False


class TestExtractor:
    def test_raises_if_no_sources_provided(self) -> None:
        with pytest.raises(ValueError):
            Extractor([])

    def test_is_available_with_at_least_one_available_source(self) -> None:
        assert Extractor([_Unavailable(), _Available(["x"])]).is_available() is True

    def test_is_unavailable_when_all_sources_down(self) -> None:
        assert Extractor([_Unavailable(), _Unavailable()]).is_available() is False

    def test_raises_when_all_sources_unavailable(self) -> None:
        with pytest.raises(DataSourceUnavailableError):
            list(Extractor([_Unavailable()]).read_chunks(date(2024, 1, 15)))

    def test_delegates_to_first_available_source(self) -> None:
        extractor = Extractor([_Unavailable(), _Available(["src-a", "src-b"])])
        chunks = list(extractor.read_chunks(date(2024, 1, 15)))
        assert len(chunks) == 1
        assert list(chunks[0]["id"]) == ["src-a", "src-b"]

    def test_skips_unavailable_sources(self) -> None:
        extractor = Extractor([_Unavailable(), _Unavailable(), _Available(["ok"])])
        chunks = list(extractor.read_chunks(date(2024, 1, 15)))
        assert len(chunks) == 1
