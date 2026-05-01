"""PostgreSQL storage adapter using psycopg2 for reliable bulk inserts."""
from __future__ import annotations

import pandas as pd
import psycopg2
import psycopg2.extras
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from finstream.domain.exceptions import DataStorageError
from finstream.interfaces.i_data_storage import IDataStorage


class PostgreSQLStorage(IDataStorage):
    """Write processed DataFrame chunks to PostgreSQL via psycopg2 bulk insert."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        url = engine.url
        self._conn_params = {
            "host":     url.host,
            "port":     url.port or 5432,
            "dbname":   url.database,
            "user":     url.username,
            "password": url.password,
        }

    def write_chunk(self, df: pd.DataFrame, table: str) -> None:
        """Append a DataFrame chunk to a PostgreSQL table.

        Uses psycopg2 execute_values for reliable bulk insert with
        explicit transaction commit.

        Args:
            df: Processed DataFrame chunk to persist.
            table: Target table name.

        Raises:
            DataStorageError: if the insert fails.
        """
        if df.empty:
            return

        clean = df.copy()
        for col in clean.select_dtypes(include="category").columns:
            clean[col] = clean[col].astype(object)
        # Convert numpy types to Python natives
        clean = clean.where(pd.notnull(clean), None)

        columns = list(clean.columns)
        rows = [tuple(row) for row in clean.itertuples(index=False, name=None)]
        cols_sql = ", ".join(f'"{c}"' for c in columns)
        sql = f'INSERT INTO "{table}" ({cols_sql}) VALUES %s ON CONFLICT DO NOTHING'

        try:
            conn = psycopg2.connect(**self._conn_params)
            try:
                with conn.cursor() as cur:
                    psycopg2.extras.execute_values(cur, sql, rows)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        except psycopg2.Error as exc:
            raise DataStorageError(table, str(exc)) from exc

    def is_available(self) -> bool:
        """Return True if the database accepts connections."""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False
