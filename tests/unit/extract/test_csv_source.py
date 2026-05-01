from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from finstream.domain.exceptions import DataSourceUnavailableError
from finstream.extract.csv_source import CSVSource


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    df = pd.DataFrame({
        "id":       ["tx-001", "tx-002", "tx-003"],
        "amount":   [100.0, 200.0, 300.0],
        "currency": ["EUR", "USD", "GBP"],
        "entity":   ["E001", "E002", "E003"],
        "date":     ["2024-01-15", "2024-01-15", "2024-01-16"],
        "source":   ["csv"] * 3,
    })
    path = tmp_path / "transactions.csv"
    df.to_csv(path, index=False)
    return path


class TestCSVSource:
    def test_is_available_when_file_exists(self, sample_csv: Path) -> None:
        assert CSVSource(sample_csv).is_available() is True

    def test_is_unavailable_when_file_missing(self, tmp_path: Path) -> None:
        assert CSVSource(tmp_path / "missing.csv").is_available() is False

    def test_raises_when_file_missing(self, tmp_path: Path) -> None:
        with pytest.raises(DataSourceUnavailableError):
            list(CSVSource(tmp_path / "missing.csv").read_chunks(date(2024, 1, 15)))

    def test_yields_rows_matching_date(self, sample_csv: Path) -> None:
        chunks = list(CSVSource(sample_csv).read_chunks(date(2024, 1, 15)))
        total = sum(len(c) for c in chunks)
        assert total == 2

    def test_no_chunks_when_no_rows_match_date(self, sample_csv: Path) -> None:
        chunks = list(CSVSource(sample_csv).read_chunks(date(2025, 6, 1)))
        assert len(chunks) == 0

    def test_chunk_has_required_columns(self, sample_csv: Path) -> None:
        chunks = list(CSVSource(sample_csv).read_chunks(date(2024, 1, 15)))
        assert len(chunks) > 0
        for col in ["id", "amount", "currency", "entity", "date", "source"]:
            assert col in chunks[0].columns

    def test_accepts_path_object(self, sample_csv: Path) -> None:
        chunks = list(CSVSource(sample_csv).read_chunks(date(2024, 1, 15)))
        assert len(chunks) > 0

    def test_accepts_string_path(self, sample_csv: Path) -> None:
        chunks = list(CSVSource(str(sample_csv)).read_chunks(date(2024, 1, 15)))
        assert len(chunks) > 0
