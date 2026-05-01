"""Integration tests for PostgreSQLStorage — requires a running PostgreSQL."""
import os

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from finstream.load.postgresql_storage import PostgreSQLStorage

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://finstream:changeme@localhost:5432/finstream")


@pytest.fixture(scope="module")
def engine():
    return create_engine(DATABASE_URL)


@pytest.fixture(scope="module")
def storage(engine):
    return PostgreSQLStorage(engine)


@pytest.fixture(autouse=True)
def clean_test_rows(engine):
    """Remove test rows before and after each test."""
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM transactions WHERE source = 'integration_test'"))
    yield
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM transactions WHERE source = 'integration_test'"))


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "id":       ["INTTEST-001", "INTTEST-002", "INTTEST-003"],
        "amount":   [1000.0, 2000.0, 3000.0],
        "currency": ["EUR", "USD", "GBP"],
        "entity":   ["Apple", "LVMH", "Airbus"],
        "date":     ["2024-01-02", "2024-01-02", "2024-01-02"],
        "source":   ["integration_test", "integration_test", "integration_test"],
    })


class TestPostgreSQLStorageIntegration:
    def test_is_available(self, storage):
        assert storage.is_available() is True

    def test_write_chunk_persists_rows(self, storage, sample_df, engine):
        storage.write_chunk(sample_df, table="transactions")
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM transactions WHERE source = 'integration_test'")
            )
            assert result.scalar() == 3

    def test_write_chunk_correct_values(self, storage, sample_df, engine):
        storage.write_chunk(sample_df, table="transactions")
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, entity, amount FROM transactions WHERE id = 'INTTEST-001'")
            )
            row = result.fetchone()
        assert row is not None
        assert row[1] == "Apple"
        assert float(row[2]) == pytest.approx(1000.0, rel=1e-3)

    def test_write_multiple_chunks(self, storage, engine):
        chunk1 = pd.DataFrame({
            "id": ["INTTEST-C1-001"], "amount": [100.0],
            "currency": ["EUR"], "entity": ["E1"],
            "date": ["2024-01-03"], "source": ["integration_test"],
        })
        chunk2 = pd.DataFrame({
            "id": ["INTTEST-C2-001"], "amount": [200.0],
            "currency": ["USD"], "entity": ["E2"],
            "date": ["2024-01-03"], "source": ["integration_test"],
        })
        storage.write_chunk(chunk1, table="transactions")
        storage.write_chunk(chunk2, table="transactions")
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM transactions WHERE source = 'integration_test'")
            )
            assert result.scalar() == 2

    def test_duplicate_ids_are_ignored(self, storage, sample_df, engine):
        storage.write_chunk(sample_df, table="transactions")
        storage.write_chunk(sample_df, table="transactions")
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM transactions WHERE source = 'integration_test'")
            )
            assert result.scalar() == 3

    def test_category_dtype_is_written_correctly(self, storage, engine):
        df = pd.DataFrame({
            "id":       pd.Categorical(["INTTEST-CAT-001"]),
            "amount":   [500.0],
            "currency": pd.Categorical(["EUR"]),
            "entity":   pd.Categorical(["TestCorp"]),
            "date":     ["2024-01-02"],
            "source":   pd.Categorical(["integration_test"]),
        })
        storage.write_chunk(df, table="transactions")
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM transactions WHERE id = 'INTTEST-CAT-001'")
            )
            assert result.scalar() == 1

    def test_empty_dataframe_writes_nothing(self, storage, engine):
        empty = pd.DataFrame(columns=["id", "amount", "currency", "entity", "date", "source"])
        storage.write_chunk(empty, table="transactions")
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM transactions WHERE source = 'integration_test'")
            )
            assert result.scalar() == 0
