"""Integration tests — full ETL pipeline writing to PostgreSQL."""
import os
from datetime import date

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from finstream.extract.fake_source import FakeDataSource
from finstream.load.postgresql_storage import PostgreSQLStorage
from finstream.pipeline.etl_pipeline import ETLPipeline

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://finstream:changeme@localhost:5432/finstream",
)

BUSINESS_DATE = date(2024, 1, 15)


@pytest.fixture(scope="module")
def engine():
    return create_engine(DATABASE_URL)


@pytest.fixture(autouse=True)
def clean_test_rows(engine):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM transactions WHERE source = 'etl_test'"))
    yield
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM transactions WHERE source = 'etl_test'"))


@pytest.fixture
def clean_df() -> pd.DataFrame:
    return pd.DataFrame({
        "id":       [f"ETL-TEST-{i:03d}" for i in range(20)],
        "amount":   [float(100 + i * 10) for i in range(20)],
        "currency": ["EUR"] * 10 + ["USD"] * 10,
        "entity":   [f"Corp{i % 5}" for i in range(20)],
        "date":     [str(BUSINESS_DATE)] * 20,
        "source":   ["etl_test"] * 20,
    })


class TestETLWritesToDatabase:
    def test_pipeline_writes_records_to_db(self, engine, clean_df):
        storage = PostgreSQLStorage(engine)
        source = FakeDataSource(clean_df)
        pipeline = ETLPipeline(source=source, storage=storage)

        pipeline.run(BUSINESS_DATE)

        with engine.connect() as conn:
            count = conn.execute(
                text("SELECT COUNT(*) FROM transactions WHERE source = 'etl_test'")
            ).scalar()
        assert count == 20

    def test_pipeline_converts_currencies_before_writing(self, engine, clean_df):
        storage = PostgreSQLStorage(engine)
        source = FakeDataSource(clean_df)
        pipeline = ETLPipeline(source=source, storage=storage)

        pipeline.run(BUSINESS_DATE)

        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT DISTINCT currency FROM transactions WHERE source = 'etl_test'")
            ).fetchall()
        currencies = {r[0] for r in rows}
        assert currencies == {"EUR"}

    def test_pipeline_removes_duplicates_before_writing(self, engine, clean_df):
        df_with_dupes = pd.concat([clean_df, clean_df.iloc[:5]], ignore_index=True)
        storage = PostgreSQLStorage(engine)
        source = FakeDataSource(df_with_dupes)
        pipeline = ETLPipeline(source=source, storage=storage)

        pipeline.run(BUSINESS_DATE)

        with engine.connect() as conn:
            count = conn.execute(
                text("SELECT COUNT(*) FROM transactions WHERE source = 'etl_test'")
            ).scalar()
        assert count == 20

    def test_pipeline_report_matches_db_count(self, engine, clean_df):
        storage = PostgreSQLStorage(engine)
        source = FakeDataSource(clean_df)
        pipeline = ETLPipeline(source=source, storage=storage)

        report = pipeline.run(BUSINESS_DATE)

        with engine.connect() as conn:
            count = conn.execute(
                text("SELECT COUNT(*) FROM transactions WHERE source = 'etl_test'")
            ).scalar()
        assert count == report.total_records

    def test_pipeline_quality_score_100_on_clean_data(self, engine, clean_df):
        storage = PostgreSQLStorage(engine)
        source = FakeDataSource(clean_df)
        pipeline = ETLPipeline(source=source, storage=storage)

        report = pipeline.run(BUSINESS_DATE)

        assert report.quality_score == 100.0

    def test_amounts_are_correctly_stored(self, engine):
        df = pd.DataFrame({
            "id":       ["ETL-TEST-AMT-001"],
            "amount":   [1000.0],
            "currency": ["USD"],
            "entity":   ["TestCorp"],
            "date":     [str(BUSINESS_DATE)],
            "source":   ["etl_test"],
        })
        storage = PostgreSQLStorage(engine)
        source = FakeDataSource(df)
        pipeline = ETLPipeline(source=source, storage=storage)

        pipeline.run(BUSINESS_DATE)

        with engine.connect() as conn:
            amount = conn.execute(
                text("SELECT amount FROM transactions WHERE id = 'ETL-TEST-AMT-001'")
            ).scalar()
        # USD 1000 * 0.92 = EUR 920 (CurrencyNormalizer default rate)
        assert float(amount) == pytest.approx(920.0, rel=1e-2)
