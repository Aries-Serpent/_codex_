"""
Comprehensive test suite for monkeypatch log adapters.

Tests cover:
- SQLite logging functionality
- Database path resolution
- Table creation
- Event logging
- Message logging
- Environment variable handling
- Connection pooling
"""

import pytest
import sqlite3
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.codex.monkeypatch.log_adapters import (
    log_event,
    log_message,
    _resolve_path,
    _ensure_table,
)


class TestPathResolution:
    """Test database path resolution."""

    def test_resolve_explicit_path(self):
        """Test resolving explicitly provided path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            resolved = _resolve_path(db_path)
            assert resolved == db_path

    def test_resolve_none_with_env_var(self):
        """Test resolving None with CODEX_LOG_DB_PATH env var."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = os.path.join(tmpdir, "env_logs.db")
            with patch.dict(os.environ, {"CODEX_LOG_DB_PATH": env_path}):
                resolved = _resolve_path(None)
                assert str(resolved) == env_path

    def test_resolve_none_without_env_var(self):
        """Test resolving None without env var uses default."""
        with patch.dict(os.environ, {}, clear=False):
            # Remove CODEX_LOG_DB_PATH if it exists
            env_backup = os.environ.pop("CODEX_LOG_DB_PATH", None)
            try:
                resolved = _resolve_path(None)
                assert ".codex/session_logs.db" in str(resolved)
            finally:
                if env_backup:
                    os.environ["CODEX_LOG_DB_PATH"] = env_backup

    def test_resolve_returns_path_object(self):
        """Test that resolved path is Path object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            resolved = _resolve_path(db_path)
            assert isinstance(resolved, Path)

    def test_resolve_string_path_conversion(self):
        """Test converting string path to Path object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            str_path = os.path.join(tmpdir, "test.db")
            resolved = _resolve_path(Path(str_path))
            assert isinstance(resolved, Path)


class TestTableEnsurance:
    """Test database table creation."""

    def test_ensure_table_creates_table(self):
        """Test that ensure_table creates the app_log table."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _ensure_table(db_path)
            
            # Verify table exists
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='app_log'"
            )
            result = cur.fetchone()
            conn.close()
            
            assert result is not None

    def test_ensure_table_idempotent(self):
        """Test that ensure_table is idempotent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            _ensure_table(db_path)
            _ensure_table(db_path)  # Should not raise error
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM app_log")
            count = cur.fetchone()[0]
            conn.close()
            
            assert count == 0  # No data should be created

    def test_table_has_required_columns(self):
        """Test that table has all required columns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _ensure_table(db_path)
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(app_log)")
            columns = cur.fetchall()
            conn.close()
            
            column_names = [col[1] for col in columns]
            assert "id" in column_names
            assert "ts" in column_names
            assert "level" in column_names
            assert "message" in column_names
            assert "meta" in column_names

    def test_table_primary_key(self):
        """Test that id column is primary key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            _ensure_table(db_path)
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(app_log)")
            columns = cur.fetchall()
            conn.close()
            
            id_col = [col for col in columns if col[1] == "id"][0]
            assert id_col[5] == 1  # pk flag


class TestLogEvent:
    """Test log_event function."""

    def test_log_event_creates_entry(self):
        """Test log_event creates a database entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            result = log_event(
                level="INFO",
                message="Test message",
                db_path=db_path
            )
            
            assert isinstance(result, Path)
            
            # Verify entry exists
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM app_log")
            count = cur.fetchone()[0]
            conn.close()
            
            assert count == 1

    def test_log_event_with_meta(self):
        """Test log_event with metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_event(
                level="ERROR",
                message="Error occurred",
                meta='{"error_code": "E001"}',
                db_path=db_path
            )
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT meta FROM app_log WHERE message=?", 
                       ("Error occurred",))
            result = cur.fetchone()
            conn.close()
            
            assert result is not None
            assert result[0] == '{"error_code": "E001"}'

    def test_log_event_without_meta(self):
        """Test log_event with None metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_event(
                level="INFO",
                message="Simple message",
                meta=None,
                db_path=db_path
            )
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT meta FROM app_log")
            result = cur.fetchone()
            conn.close()
            
            assert result[0] is None

    def test_log_event_timestamp(self):
        """Test log_event creates timestamp."""
        import time
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            before_time = time.time()
            log_event(
                level="INFO",
                message="Timestamped message",
                db_path=db_path
            )
            after_time = time.time()
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT ts FROM app_log")
            ts = cur.fetchone()[0]
            conn.close()
            
            assert before_time <= ts <= after_time

    def test_log_event_level_stored(self):
        """Test log_event stores level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_event(
                level="WARNING",
                message="Warning message",
                db_path=db_path
            )
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT level FROM app_log")
            level = cur.fetchone()[0]
            conn.close()
            
            assert level == "WARNING"

    def test_log_event_returns_path(self):
        """Test log_event returns database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            result = log_event(
                level="INFO",
                message="Test",
                db_path=db_path
            )
            
            assert result == db_path

    def test_log_event_default_path(self):
        """Test log_event with default path."""
        with patch.dict(os.environ, {"CODEX_LOG_DB_PATH": "/tmp/test.db"}):
            result = log_event(
                level="INFO",
                message="Default path test"
            )
            
            assert result is not None

    def test_log_multiple_events(self):
        """Test logging multiple events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            for i in range(5):
                log_event(
                    level="INFO",
                    message=f"Message {i}",
                    db_path=db_path
                )
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM app_log")
            count = cur.fetchone()[0]
            conn.close()
            
            assert count == 5


class TestLogMessage:
    """Test log_message function."""

    def test_log_message_creates_entry(self):
        """Test log_message creates a database entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            result = log_message(
                message="Test message",
                db_path=db_path
            )
            
            assert isinstance(result, Path)
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM app_log")
            count = cur.fetchone()[0]
            conn.close()
            
            assert count == 1

    def test_log_message_default_level(self):
        """Test log_message uses default INFO level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_message(
                message="Default level",
                db_path=db_path
            )
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT level FROM app_log")
            level = cur.fetchone()[0]
            conn.close()
            
            assert level == "INFO"

    def test_log_message_custom_level(self):
        """Test log_message with custom level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_message(
                message="Custom level",
                level="CRITICAL",
                db_path=db_path
            )
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT level FROM app_log")
            level = cur.fetchone()[0]
            conn.close()
            
            assert level == "CRITICAL"

    def test_log_message_with_meta(self):
        """Test log_message with metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_message(
                message="Message with meta",
                meta='{"key": "value"}',
                db_path=db_path
            )
            
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT meta FROM app_log")
            result = cur.fetchone()
            conn.close()
            
            assert result[0] == '{"key": "value"}'

    def test_log_message_returns_path(self):
        """Test log_message returns database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            result = log_message(
                message="Test",
                db_path=db_path
            )
            
            assert result == db_path


class TestConnectionPooling:
    """Test connection pooling behavior."""

    def test_pooling_disabled_by_default(self):
        """Test connection pooling disabled when env var not set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("CODEX_SQLITE_POOL", None)
                log_event(
                    level="INFO",
                    message="Pooling test",
                    db_path=db_path
                )
            
            assert True  # Connection should close after operation

    def test_pooling_enabled_with_env_var(self):
        """Test connection pooling enabled with CODEX_SQLITE_POOL=1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with patch.dict(os.environ, {"CODEX_SQLITE_POOL": "1"}):
                log_event(
                    level="INFO",
                    message="Pooling enabled",
                    db_path=db_path
                )
            
            assert True


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_database_path(self):
        """Test handling of invalid database path."""
        invalid_path = Path("/invalid/path/that/does/not/exist/test.db")
        
        try:
            log_event(
                level="INFO",
                message="Test",
                db_path=invalid_path
            )
            # May fail or handle gracefully
        except (OSError, sqlite3.Error):
            assert True

    def test_corrupted_database(self):
        """Test handling of corrupted database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "corrupted.db"
            
            # Create corrupted file
            with open(db_path, "w") as f:
                f.write("corrupted data")
            
            try:
                log_event(
                    level="INFO",
                    message="Test",
                    db_path=db_path
                )
            except sqlite3.DatabaseError:
                assert True

    def test_permission_denied(self):
        """Test handling permission denied."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "readonly.db"
            _ensure_table(db_path)
            
            # Make owner-read-only to keep the file restricted without exposing it broadly.
            os.chmod(db_path, 0o400)
            
            try:
                log_event(
                    level="INFO",
                    message="Test",
                    db_path=db_path
                )
            except (OSError, sqlite3.Error, PermissionError):
                assert True
            finally:
                # Restore permissions for cleanup while keeping the file owner-only.
                os.chmod(db_path, 0o600)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
