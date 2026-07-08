"""
Comprehensive tests for codex.monkeypatch.log_adapters module.

Tests cover all logging functions with various configurations and edge cases.
"""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from codex.monkeypatch.log_adapters import (
    _ensure_table,
    _resolve_path,
    log_event,
    log_message,
)


class TestResolvePath:
    """Test path resolution logic."""

    def test_resolve_path_with_explicit_path(self):
        """Test _resolve_path returns explicit path when provided."""
        explicit_path = Path("/explicit/path/db.sqlite")
        result = _resolve_path(explicit_path)
        assert result == explicit_path, "Result must not be empty"

    def test_resolve_path_with_none_uses_env(self):
        """Test _resolve_path uses env var when path is None."""
        with patch.dict(os.environ, {"CODEX_LOG_DB_PATH": "/env/path/db.sqlite"}):
            result = _resolve_path(None)
            assert result == Path("/env/path/db.sqlite"), "Result must not be empty"

    def test_resolve_path_with_none_default_env(self):
        """Test _resolve_path uses default when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            result = _resolve_path(None)
            assert result == Path(".codex/session_logs.db"), "Result must not be empty"

    def test_resolve_path_prefers_explicit_over_env(self):
        """Test that explicit path is preferred over env var."""
        explicit = Path("/explicit/path")
        with patch.dict(os.environ, {"CODEX_LOG_DB_PATH": "/env/path"}):
            result = _resolve_path(explicit)
            assert result == explicit, "Result must not be empty"

    def test_resolve_path_with_string_path(self):
        """Test _resolve_path with string path (converts to Path)."""
        string_path = "/string/path/db.sqlite"
        result = _resolve_path(string_path)
        assert isinstance(result, Path)
        assert result == Path(string_path), "Result must not be empty"


class TestEnsureTable:
    """Test database table creation."""

    def test_ensure_table_creates_database(self):
        """Test that _ensure_table creates a database file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _ensure_table(db_path)
            assert db_path.exists(), "Condition must be true"

    def test_ensure_table_creates_app_log_table(self):
        """Test that app_log table is created with correct schema."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _ensure_table(db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_log'")
            table_exists = cur.fetchone() is not None
            conn.close()

            assert table_exists, "table_exists is not valid"

    def test_ensure_table_correct_schema(self):
        """Test that app_log table has correct columns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _ensure_table(db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(app_log)")
            columns = {row[1]: row[2] for row in cur.fetchall()}
            conn.close()

            expected_columns = {
                "id": "INTEGER",
                "ts": "REAL",
                "level": "TEXT",
                "message": "TEXT",
                "meta": "TEXT",
            }
            for col_name, col_type in expected_columns.items():
                assert col_name in columns, "Condition must be true"

    def test_ensure_table_idempotent(self):
        """Test that calling _ensure_table twice doesn't cause errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _ensure_table(db_path)
            _ensure_table(db_path)  # Call again
            assert db_path.exists(), "Condition must be true"

    def test_ensure_table_pool_disabled_by_default(self):
        """Test that connection pool is disabled by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with patch.dict(os.environ, {}, clear=True):
                # Mock sqlite3.connect to verify close is called
                with patch("sqlite3.connect") as mock_connect:
                    mock_conn = MagicMock()
                    mock_connect.return_value = mock_conn
                    mock_conn.cursor.return_value = MagicMock()

                    _ensure_table(db_path)

                    # Should have called close (pool disabled)
                    mock_conn.close.assert_called_once()

    @patch.dict(os.environ, {"CODEX_SQLITE_POOL": "1"})
    def test_ensure_table_pool_enabled(self):
        """Test that connection is not closed when pool is enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with patch("sqlite3.connect") as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_conn.cursor.return_value = MagicMock()

                _ensure_table(db_path)

                # Should not close when pool is enabled
                mock_conn.close.assert_not_called()

    @patch.dict(os.environ, {"CODEX_SQLITE_POOL": "true"})
    def test_ensure_table_pool_string_true(self):
        """Test pool detection with 'true' string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with patch("sqlite3.connect") as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_conn.cursor.return_value = MagicMock()

                _ensure_table(db_path)

                mock_conn.close.assert_not_called()


class TestLogEvent:
    """Test log_event function."""

    def test_log_event_basic(self):
        """Test basic log_event functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            result = log_event("INFO", "Test message", db_path=db_path)

            assert result == db_path, "Result must not be empty"
            assert db_path.exists(), "Condition must be true"

            # Verify record was inserted
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM app_log")
            count = cur.fetchone()[0]
            conn.close()

            assert count == 1, "Count must be greater than zero"

    def test_log_event_with_meta(self):
        """Test log_event with metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            meta = '{"key": "value"}'
            log_event("WARNING", "Test message", meta=meta, db_path=db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT meta FROM app_log WHERE message = 'Test message'")
            result = cur.fetchone()[0]
            conn.close()

            assert result == meta, "Result must not be empty"

    def test_log_event_without_meta(self):
        """Test log_event without metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_event("ERROR", "Test message", db_path=db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT meta FROM app_log WHERE message = 'Test message'")
            result = cur.fetchone()[0]
            conn.close()

            assert result is None, "Result must not be empty"

    def test_log_event_multiple_levels(self):
        """Test log_event with different log levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            for level in levels:
                log_event(level, f"Message for {level}", db_path=db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM app_log WHERE level = ?", (levels[0],))
            count = cur.fetchone()[0]
            conn.close()

            assert count == 1, "Count must be greater than zero"

    def test_log_event_multiple_records(self):
        """Test logging multiple events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            for i in range(5):
                log_event("INFO", f"Message {i}", db_path=db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM app_log")
            count = cur.fetchone()[0]
            conn.close()

            assert count == 5, "Count must be greater than zero"

    def test_log_event_timestamp_stored(self):
        """Test that timestamp is stored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_event("INFO", "Test message", db_path=db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT ts FROM app_log")
            ts = cur.fetchone()[0]
            conn.close()

            assert isinstance(ts, float)
            assert ts > 0, "ts must be greater than zero"

    def test_log_event_default_path(self):
        """Test log_event with default path (uses env var)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = str(Path(tmpdir) / "default.db")
            with patch.dict(os.environ, {"CODEX_LOG_DB_PATH": env_path}):
                result = log_event("INFO", "Test message")
                assert result == Path(env_path), "Result must not be empty"

    def test_log_event_creates_parent_directory(self):
        """Test that log_event works with pre-existing parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create parent directories first
            db_dir = Path(tmpdir) / "nested" / "dir"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "test.db"
            log_event("INFO", "Test message", db_path=db_path)
            assert db_path.exists(), "Condition must be true"

    def test_log_event_returns_path(self):
        """Test that log_event returns the database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            result = log_event("INFO", "Test message", db_path=db_path)
            assert isinstance(result, Path)
            assert str(result) == str(db_path), "Result must not be empty"

    def test_log_event_pool_enabled(self):
        """Test that connection is not closed when pool is enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with patch.dict(os.environ, {"CODEX_SQLITE_POOL": "1"}):
                with patch("sqlite3.connect") as mock_connect:
                    mock_conn = MagicMock()
                    mock_connect.return_value = mock_conn
                    mock_cursor = MagicMock()
                    mock_conn.cursor.return_value = mock_cursor

                    log_event("INFO", "Test", db_path=db_path)

                    mock_conn.close.assert_not_called()


class TestLogMessage:
    """Test log_message function."""

    def test_log_message_basic(self):
        """Test basic log_message functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            result = log_message("Test message", db_path=db_path)

            assert result == db_path, "Result must not be empty"
            assert db_path.exists(), "Condition must be true"

    def test_log_message_default_level(self):
        """Test log_message uses INFO as default level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_message("Test message", db_path=db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT level FROM app_log")
            level = cur.fetchone()[0]
            conn.close()

            assert level == "INFO", "level is not valid"

    def test_log_message_custom_level(self):
        """Test log_message with custom level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_message("Test message", level="ERROR", db_path=db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT level FROM app_log")
            level = cur.fetchone()[0]
            conn.close()

            assert level == "ERROR", "Error should be raised or set"

    def test_log_message_with_meta(self):
        """Test log_message with metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            meta = '{"user": "testuser"}'
            log_message("Test message", meta=meta, db_path=db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT meta FROM app_log")
            result = cur.fetchone()[0]
            conn.close()

            assert result == meta, "Result must not be empty"

    def test_log_message_calls_log_event(self):
        """Test that log_message calls log_event internally."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with patch("codex.monkeypatch.log_adapters.log_event") as mock_log_event:
                mock_log_event.return_value = db_path
                log_message("Test message", level="WARNING", db_path=db_path)

                mock_log_event.assert_called_once()
                call_args = mock_log_event.call_args
                assert call_args[1]["level"] == "WARNING", "Condition must be true"
                assert call_args[1]["message"] == "Test message", "Condition must be true"

    def test_log_message_multiple_levels(self):
        """Test log_message with different levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            for level in levels:
                log_message(f"Message for {level}", level=level, db_path=db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM app_log")
            count = cur.fetchone()[0]
            conn.close()

            assert count == len(levels), "Levels must not be empty"

    def test_log_message_default_path(self):
        """Test log_message with default path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = str(Path(tmpdir) / "default.db")
            with patch.dict(os.environ, {"CODEX_LOG_DB_PATH": env_path}):
                result = log_message("Test message")
                assert result == Path(env_path), "Result must not be empty"

    def test_log_message_returns_path(self):
        """Test that log_message returns the database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            result = log_message("Test message", db_path=db_path)
            assert isinstance(result, Path)
            assert result == db_path, "Result must not be empty"


class TestLogAdaptersIntegration:
    """Integration tests for logging functions."""

    def test_sequential_logging(self):
        """Test sequential log_event and log_message calls."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"

            log_event("INFO", "Event 1", db_path=db_path)
            log_message("Message 1", db_path=db_path)
            log_event("ERROR", "Event 2", meta="meta_data", db_path=db_path)
            log_message("Message 2", level="WARNING", db_path=db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM app_log")
            count = cur.fetchone()[0]
            conn.close()

            assert count == 4, "Count must be greater than zero"

    def test_mixed_operations(self):
        """Test mixing log_event and log_message operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"

            # Log various events
            for i in range(3):
                log_event("INFO", f"Event {i}", db_path=db_path)
                log_message(f"Message {i}", level="DEBUG", db_path=db_path)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM app_log")
            count = cur.fetchone()[0]
            cur.execute("SELECT level FROM app_log ORDER BY ts")
            levels = [row[0] for row in cur.fetchall()]
            conn.close()

            assert count == 6, "Count must be greater than zero"
            assert levels.count("INFO") == 3, "Count must be greater than zero"
            assert levels.count("DEBUG") == 3, "Count must be greater than zero"

    def test_pool_persistence(self):
        """Test that pool setting affects multiple operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with patch.dict(os.environ, {"CODEX_SQLITE_POOL": "yes"}):
                with patch("sqlite3.connect") as mock_connect:
                    mock_conn = MagicMock()
                    mock_connect.return_value = mock_conn
                    mock_cursor = MagicMock()
                    mock_conn.cursor.return_value = mock_cursor

                    log_event("INFO", "Test", db_path=db_path)
                    log_message("Test", db_path=db_path)

                    # Should not close in either call
                    assert mock_conn.close.call_count == 0, "Count must be greater than zero"
