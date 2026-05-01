"""Unit tests for PostgreSQLStorage — mocked psycopg2, no real DB."""
from unittest.mock import MagicMock, patch, call
import pandas as pd
import pytest

from finstream.domain.exceptions import DataStorageError
from finstream.load.postgresql_storage import PostgreSQLStorage


@pytest.fixture
def mock_engine():
    engine = MagicMock()
    engine.url.render_as_string.return_value = "postgresql://user:pass@localhost/test"
    return engine


@pytest.fixture
def storage(mock_engine):
    return PostgreSQLStorage(mock_engine)


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "id":       ["tx-001", "tx-002"],
        "amount":   [100.0, 200.0],
        "currency": ["EUR", "USD"],
        "entity":   ["Apple", "LVMH"],
        "date":     ["2024-01-02", "2024-01-02"],
        "source":   ["yahoo", "yahoo"],
    })


class TestWriteChunk:
    def test_empty_dataframe_does_nothing(self, storage):
        empty = pd.DataFrame(columns=["id", "amount", "currency", "entity", "date", "source"])
        with patch("psycopg2.connect") as mock_connect:
            storage.write_chunk(empty, table="transactions")
            mock_connect.assert_not_called()

    def test_calls_execute_values_with_correct_table(self, storage, sample_df):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        with patch("psycopg2.connect", return_value=mock_conn):
            with patch("psycopg2.extras.execute_values") as mock_exec:
                storage.write_chunk(sample_df, table="transactions")
                assert mock_exec.called
                sql_arg = mock_exec.call_args[0][1]
                assert '"transactions"' in sql_arg

    def test_commits_after_successful_write(self, storage, sample_df):
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        with patch("psycopg2.connect", return_value=mock_conn):
            with patch("psycopg2.extras.execute_values"):
                storage.write_chunk(sample_df, table="transactions")
                mock_conn.commit.assert_called_once()

    def test_rolls_back_and_raises_on_error(self, storage, sample_df):
        import psycopg2 as pg2
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.execute_values = MagicMock(side_effect=pg2.OperationalError("DB error"))
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        with patch("psycopg2.connect", return_value=mock_conn):
            with patch("psycopg2.extras.execute_values", side_effect=pg2.OperationalError("DB error")):
                with pytest.raises(DataStorageError):
                    storage.write_chunk(sample_df, table="transactions")
                mock_conn.rollback.assert_called_once()
                mock_conn.close.assert_called_once()

    def test_closes_connection_after_write(self, storage, sample_df):
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        with patch("psycopg2.connect", return_value=mock_conn):
            with patch("psycopg2.extras.execute_values"):
                storage.write_chunk(sample_df, table="transactions")
                mock_conn.close.assert_called_once()

    def test_converts_category_columns(self, storage):
        df = pd.DataFrame({
            "id":       pd.Categorical(["tx-001"]),
            "amount":   [100.0],
            "currency": pd.Categorical(["EUR"]),
            "entity":   pd.Categorical(["Apple"]),
            "date":     ["2024-01-02"],
            "source":   pd.Categorical(["yahoo"]),
        })
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        with patch("psycopg2.connect", return_value=mock_conn):
            with patch("psycopg2.extras.execute_values") as mock_exec:
                storage.write_chunk(df, table="transactions")
                assert mock_exec.called


class TestIsAvailable:
    def test_returns_true_when_db_reachable(self, storage, mock_engine):
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        assert storage.is_available() is True

    def test_returns_false_when_db_unreachable(self, storage, mock_engine):
        from sqlalchemy.exc import OperationalError
        mock_engine.connect.side_effect = OperationalError("", "", "")
        assert storage.is_available() is False
