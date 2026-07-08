"""Tests for codex.logging.db_utils module.

Phase 7 tests covering:
- open_db function
- list_tables function
- get_columns function
- infer_probable_table function
- infer_columns function
- _sanitize_table helper
- resolve_db_path helper
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest


class TestOpenDb:
    """Tests for open_db function."""

    @pytest.fixture
    def open_db(self):
        """Import open_db function."""
        from codex.logging.db_utils import open_db

        return open_db

    @pytest.fixture
    def clean_env(self):
        """Clear database env vars for testing."""
        saved = {}
        for key in ("CODEX_DB_PATH", "CODEX_LOG_DB_PATH"):
            if key in os.environ:
                saved[key] = os.environ.pop(key)
        yield
        for key, val in saved.items():
            os.environ[key] = val

    def test_open_db_with_path(self, open_db, tmp_path):
        """Test opening database with explicit path."""
        db_path = str(tmp_path / "test.db")
        conn = open_db(db_path)
        assert conn is not None, "conn must be initialized"
        conn.close()

    def test_open_db_creates_file(self, open_db, tmp_path):
        """Test that open_db creates the database file."""
        db_path = tmp_path / "test.db"
        conn = open_db(str(db_path))
        conn.close()
        assert db_path.exists(), "Condition must be true"

    def test_open_db_from_env_var(self, open_db, tmp_path, clean_env):
        """Test opening database from environment variable."""
        db_path = str(tmp_path / "env_test.db")
        os.environ["CODEX_DB_PATH"] = db_path

        conn = open_db()
        assert conn is not None, "conn must be initialized"
        conn.close()

    def test_open_db_fallback_to_memory(self, open_db, clean_env):
        """Test fallback to in-memory database."""
        # With no path, no env vars, and no existing files
        conn = open_db()
        assert conn is not None, "conn must be initialized"
        # In-memory databases still work
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.close()


class TestSanitizeTable:
    """Tests for _sanitize_table function."""

    @pytest.fixture
    def sanitize(self):
        """Import _sanitize_table function."""
        from codex.logging.db_utils import _sanitize_table

        return _sanitize_table

    def test_valid_simple_name(self, sanitize):
        """Test valid simple table name."""
        assert sanitize("users") == "users", "Condition must be true"

    def test_valid_name_with_numbers(self, sanitize):
        """Test valid name with numbers."""
        assert sanitize("table123") == "table123", "Condition must be true"

    def test_valid_name_with_underscore(self, sanitize):
        """Test valid name with underscore."""
        assert sanitize("my_table") == "my_table", "Condition must be true"

    def test_valid_name_starting_with_underscore(self, sanitize):
        """Test valid name starting with underscore."""
        assert sanitize("_private") == "_private", "Condition must be true"

    def test_invalid_name_with_hyphen(self, sanitize):
        """Test invalid name with hyphen."""
        with pytest.raises(ValueError, match="Unsafe table name"):
            sanitize("my-table")

    def test_invalid_name_with_space(self, sanitize):
        """Test invalid name with space."""
        with pytest.raises(ValueError, match="Unsafe table name"):
            sanitize("my table")

    def test_invalid_name_starting_with_number(self, sanitize):
        """Test invalid name starting with number."""
        with pytest.raises(ValueError, match="Unsafe table name"):
            sanitize("123table")

    def test_invalid_name_with_special_chars(self, sanitize):
        """Test invalid name with special characters."""
        with pytest.raises(ValueError, match="Unsafe table name"):
            sanitize("table;DROP")


class TestListTables:
    """Tests for list_tables function."""

    @pytest.fixture
    def list_tables(self):
        """Import list_tables function."""
        from codex.logging.db_utils import list_tables

        return list_tables

    def test_list_tables_empty_db(self, list_tables):
        """Test listing tables in empty database."""
        conn = sqlite3.connect(":memory:")
        tables = list_tables(conn)
        assert tables == [], "tables is not valid"
        conn.close()

    def test_list_tables_with_tables(self, list_tables):
        """Test listing tables in database with tables."""
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE users (id INTEGER)")
        conn.execute("CREATE TABLE logs (id INTEGER)")

        tables = list_tables(conn)

        assert "users" in tables, "Condition must be true"
        assert "logs" in tables, "Condition must be true"
        assert len(tables) == 2, "Tables must not be empty"
        conn.close()


class TestGetColumns:
    """Tests for get_columns function."""

    @pytest.fixture
    def get_columns(self):
        """Import get_columns function."""
        from codex.logging.db_utils import get_columns

        return get_columns

    def test_get_columns_basic(self, get_columns):
        """Test getting columns from table."""
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE users (id INTEGER, name TEXT, email TEXT)")

        columns = get_columns(conn, "users")

        assert "id" in columns, "Condition must be true"
        assert "name" in columns, "Condition must be true"
        assert "email" in columns, "Condition must be true"
        assert len(columns) == 3, "Columns must not be empty"
        conn.close()

    def test_get_columns_preserves_case(self, get_columns):
        """Test that column names preserve case."""
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE test (ID INTEGER, UserName TEXT)")

        columns = get_columns(conn, "test")

        assert "ID" in columns, "Condition must be true"
        assert "UserName" in columns, "Condition must be true"
        conn.close()


class TestInferProbableTable:
    """Tests for infer_probable_table function."""

    @pytest.fixture
    def infer_table(self):
        """Import infer_probable_table function."""
        from codex.logging.db_utils import infer_probable_table

        return infer_probable_table

    def test_infer_empty_db(self, infer_table):
        """Test inference on empty database."""
        conn = sqlite3.connect(":memory:")
        result = infer_table(conn)
        assert result is None, "Result must not be empty"
        conn.close()

    def test_infer_exact_match_session_events(self, infer_table):
        """Test preference for session_events table."""
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE random (id INTEGER)")
        conn.execute("CREATE TABLE session_events (id INTEGER, ts TEXT)")

        result = infer_table(conn)

        assert result == "session_events", "Result must not be empty"
        conn.close()

    def test_infer_exact_match_logs(self, infer_table):
        """Test preference for logs table."""
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE random (id INTEGER)")
        conn.execute("CREATE TABLE logs (id INTEGER)")

        result = infer_table(conn)

        assert result == "logs", "Result must not be empty"
        conn.close()

    def test_infer_by_column_score(self, infer_table):
        """Test inference by column scoring."""
        conn = sqlite3.connect(":memory:")
        # Create table with many logging-related columns
        conn.execute("""
            CREATE TABLE my_logs (
                id INTEGER,
                timestamp TEXT,
                message TEXT,
                role TEXT,
                session_id TEXT
            )
        """)
        conn.execute("CREATE TABLE other (id INTEGER)")

        result = infer_table(conn)

        assert result == "my_logs", "Result must not be empty"
        conn.close()


class TestInferColumns:
    """Tests for infer_columns function."""

    @pytest.fixture
    def infer_columns(self):
        """Import infer_columns function."""
        from codex.logging.db_utils import infer_columns

        return infer_columns

    def test_infer_columns_basic(self, infer_columns):
        """Test basic column inference."""
        conn = sqlite3.connect(":memory:")
        conn.execute("""
            CREATE TABLE logs (
                id INTEGER,
                timestamp TEXT,
                message TEXT,
                role TEXT
            )
        """)

        result = infer_columns(conn, "logs")

        assert result["timestamp"] == "timestamp", "Result must not be empty"
        assert result["message"] == "message", "Result must not be empty"
        assert result["role"] == "role", "Result must not be empty"
        conn.close()

    def test_infer_columns_with_variants(self, infer_columns):
        """Test inference with column name variants."""
        conn = sqlite3.connect(":memory:")
        conn.execute("""
            CREATE TABLE logs (
                id INTEGER,
                ts TEXT,
                content TEXT,
                speaker TEXT
            )
        """)

        result = infer_columns(conn, "logs")

        # Should find variants
        assert result["timestamp"] == "ts", "Result must not be empty"
        assert result["message"] == "content", "Result must not be empty"
        assert result["role"] == "speaker", "Result must not be empty"
        conn.close()


class TestResolveDbPath:
    """Tests for resolve_db_path function."""

    @pytest.fixture
    def resolve_db_path(self):
        """Import resolve_db_path function."""
        from codex.logging.db_utils import resolve_db_path

        return resolve_db_path

    def test_resolve_path_object(self, resolve_db_path, tmp_path):
        """Test resolving Path object."""
        db_path = tmp_path / "test.db"
        result = resolve_db_path(db_path)
        assert isinstance(result, Path)

    def test_resolve_string_path(self, resolve_db_path, tmp_path):
        """Test resolving string path."""
        db_path = str(tmp_path / "test.db")
        result = resolve_db_path(db_path)
        assert isinstance(result, Path)
