from datetime import date
from typing import Iterator

import pandas as pd
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from finstream.domain.exceptions import DataSourceUnavailableError
from finstream.interfaces.i_data_source import IDataSource

_QUERY = text("""
    SELECT id, amount, currency, entity, date, source
    FROM transactions
    WHERE date = :business_date
""")


class PostgreSQLSource(IDataSource):
    """Read financial transactions from PostgreSQL in chunks.

    Uses SQLAlchemy so the engine can be swapped in tests (SQLite in-memory).
    """

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def read_chunks(
        self,
        business_date: date,
        chunk_size: int = 10_000,
    ) -> Iterator[pd.DataFrame]:
        """Stream transactions for a given business date in chunks.

        Args:
            business_date: The date to filter transactions on.
            chunk_size: Number of rows per chunk.

        Yields:
            DataFrame chunks with columns: id, amount, currency, entity, date, source.

        Raises:
            DataSourceUnavailableError: if the database is unreachable.
        """
        try:
            with self._engine.connect() as conn:
                for chunk in pd.read_sql(
                    _QUERY,
                    conn,
                    params={"business_date": business_date},
                    chunksize=chunk_size,
                ):
                    yield chunk
        except SQLAlchemyError as exc:
            raise DataSourceUnavailableError("postgresql") from exc

    def is_available(self) -> bool:
        """Return True if the database accepts connections."""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False
