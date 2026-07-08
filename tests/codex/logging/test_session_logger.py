"""
Test Session Logger Module

Comprehensive unit tests for the session logging functionality.
"""

from __future__ import annotations

import os
import sqlite3
import tempfile
import threading
import time
import uuid
from pathlib import Path

import pytest


class TestSessionLoggerImports:
    """Tests for session logger module imports."""

    def test_import_module(self) -> None:
        from codex.logging import session_logger

        assert session_logger is not None, "session_logger must be initialized"

    def test_import_session_logger_class(self) -> None:
        from codex.logging.session_logger import SessionLogger

        assert SessionLogger is not None, "SessionLogger must be initialized"

    def test_import_log_message(self) -> None:
        from codex.logging.session_logger import log_message

        assert callable(log_message), "Condition must be true"

    def test_import_log_event(self) -> None:
        from codex.logging.session_logger import log_event

        assert callable(log_event), "Condition must be true"

    def test_import_init_db(self) -> None:
        from codex.logging.session_logger import init_db

        assert callable(init_db), "Condition must be true"

    def test_import_get_session_id(self) -> None:
        from codex.logging.session_logger import get_session_id

        assert callable(get_session_id), "Condition must be true"

    def test_import_fetch_messages(self) -> None:
        from codex.logging.session_logger import fetch_messages

        assert callable(fetch_messages), "Condition must be true"

    def test_import_migrate_legacy_events(self) -> None:
        from codex.logging.session_logger import migrate_legacy_events

        assert callable(migrate_legacy_events), "Condition must be true"


class TestAllowedRoles:
    """Tests for role validation."""

    def test_allowed_roles_exist(self) -> None:
        from codex.logging.session_logger import _ALLOWED_ROLES

        assert isinstance(_ALLOWED_ROLES, set)

    def test_allowed_roles_contains_system(self) -> None:
        from codex.logging.session_logger import _ALLOWED_ROLES

        assert "system" in _ALLOWED_ROLES, "Condition must be true"

    def test_allowed_roles_contains_user(self) -> None:
        from codex.logging.session_logger import _ALLOWED_ROLES

        assert "user" in _ALLOWED_ROLES, "Condition must be true"

    def test_allowed_roles_contains_assistant(self) -> None:
        from codex.logging.session_logger import _ALLOWED_ROLES

        assert "assistant" in _ALLOWED_ROLES, "Condition must be true"

    def test_allowed_roles_contains_tool(self) -> None:
        from codex.logging.session_logger import _ALLOWED_ROLES

        assert "tool" in _ALLOWED_ROLES, "Condition must be true"

    def test_allowed_roles_contains_info(self) -> None:
        from codex.logging.session_logger import _ALLOWED_ROLES

        assert "INFO" in _ALLOWED_ROLES, "Condition must be true"

    def test_allowed_roles_contains_warn(self) -> None:
        from codex.logging.session_logger import _ALLOWED_ROLES

        assert "WARN" in _ALLOWED_ROLES, "Condition must be true"


class TestGetSessionId:
    """Tests for get_session_id function."""

    def test_returns_string(self) -> None:
        from codex.logging.session_logger import get_session_id

        # Clear existing session ID
        old_id = os.environ.pop("CODEX_SESSION_ID", None)
        try:
            result = get_session_id()
            assert isinstance(result, str)
        finally:
            # Restore
            if old_id:
                os.environ["CODEX_SESSION_ID"] = old_id

    def test_returns_uuid_format(self) -> None:
        from codex.logging.session_logger import get_session_id

        old_id = os.environ.pop("CODEX_SESSION_ID", None)
        try:
            result = get_session_id()
            # Should be a valid UUID
            uuid_obj = uuid.UUID(result)
            assert str(uuid_obj) == result, "Result must not be empty"
        finally:
            if old_id:
                os.environ["CODEX_SESSION_ID"] = old_id

    def test_uses_env_var_if_set(self) -> None:
        from codex.logging.session_logger import get_session_id

        test_id = "test-session-12345"
        old_id = os.environ.get("CODEX_SESSION_ID")
        try:
            os.environ["CODEX_SESSION_ID"] = test_id
            result = get_session_id()
            assert result == test_id, "Result must not be empty"
        finally:
            if old_id:
                os.environ["CODEX_SESSION_ID"] = old_id
            else:
                os.environ.pop("CODEX_SESSION_ID", None)

    def test_sets_env_var_on_generation(self) -> None:
        from codex.logging.session_logger import get_session_id

        old_id = os.environ.pop("CODEX_SESSION_ID", None)
        try:
            result = get_session_id()
            assert os.environ.get("CODEX_SESSION_ID") == result, "Result must not be empty"
        finally:
            if old_id:
                os.environ["CODEX_SESSION_ID"] = old_id


class TestInitDb:
    """Tests for init_db function."""

    def test_creates_parent_directory(self) -> None:
        from codex.logging.session_logger import init_db

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "subdir" / "test.db"
            init_db(db_path)
            assert db_path.parent.exists(), "Condition must be true"

    def test_creates_database_file(self) -> None:
        from codex.logging.session_logger import init_db

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            init_db(db_path)
            assert db_path.exists(), "Condition must be true"

    def test_returns_path(self) -> None:
        from codex.logging.session_logger import init_db

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            result = init_db(db_path)
            assert result == db_path, "Result must not be empty"

    def test_creates_session_events_table(self) -> None:
        from codex.logging.session_logger import init_db

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            init_db(db_path)

            conn = sqlite3.connect(db_path)
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='session_events'"
            )
            tables = cursor.fetchall()
            conn.close()

            assert len(tables) == 1, "Tables must not be empty"

    def test_idempotent(self) -> None:
        from codex.logging.session_logger import INITIALIZED_PATHS, init_db

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            # Clear cached paths
            INITIALIZED_PATHS.discard(str(db_path))

            result1 = init_db(db_path)
            result2 = init_db(db_path)
            assert result1 == result2, "Result must not be empty"


class TestLogMessage:
    """Tests for log_message function."""

    def test_valid_role_user(self) -> None:
        from codex.logging.session_logger import log_message

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            # Should not raise
            log_message("test-session", "user", "Hello", db_path=db_path)

    def test_valid_role_assistant(self) -> None:
        from codex.logging.session_logger import log_message

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_message("test-session", "assistant", "Hi there", db_path=db_path)

    def test_valid_role_system(self) -> None:
        from codex.logging.session_logger import log_message

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_message("test-session", "system", "Starting", db_path=db_path)

    def test_valid_role_tool(self) -> None:
        from codex.logging.session_logger import log_message

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_message("test-session", "tool", "Tool output", db_path=db_path)

    def test_invalid_role_raises(self) -> None:
        from codex.logging.session_logger import log_message

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with pytest.raises(ValueError, match="invalid role"):
                log_message("test-session", "invalid_role", "Message", db_path=db_path)

    def test_coerces_message_to_string(self) -> None:
        from codex.logging.session_logger import fetch_messages, log_message

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_message("test-session", "user", 12345, db_path=db_path)
            messages = fetch_messages("test-session", db_path=db_path)
            assert any("12345" in msg.get("message", "") for msg in messages)


class TestSessionLoggerClass:
    """Tests for SessionLogger context manager."""

    def test_context_manager_enter(self) -> None:
        from codex.logging.session_logger import SessionLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with SessionLogger(session_id="test-ctx", db_path=db_path) as sl:
                assert sl.session_id == "test-ctx", "session_id is not valid"

    def test_context_manager_logs_start(self) -> None:
        from codex.logging.session_logger import SessionLogger, fetch_messages

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with SessionLogger(session_id="test-start", db_path=db_path):
                pass

            messages = fetch_messages("test-start", db_path=db_path)
            assert any("session_start" in msg.get("message", "") for msg in messages)

    def test_context_manager_logs_end(self) -> None:
        from codex.logging.session_logger import SessionLogger, fetch_messages

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with SessionLogger(session_id="test-end", db_path=db_path):
                pass

            messages = fetch_messages("test-end", db_path=db_path)
            assert any("session_end" in msg.get("message", "") for msg in messages)

    def test_log_method(self) -> None:
        from codex.logging.session_logger import SessionLogger, fetch_messages

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with SessionLogger(session_id="test-log", db_path=db_path) as sl:
                sl.log("user", "Test message")

            messages = fetch_messages("test-log", db_path=db_path)
            assert any("Test message" in msg.get("message", "") for msg in messages)

    def test_exception_logged(self) -> None:
        from codex.logging.session_logger import SessionLogger, fetch_messages

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            try:
                with SessionLogger(session_id="test-exc", db_path=db_path):
                    raise ValueError("Test exception")
            except ValueError:
                _ = None  # suppressed: no action needed

            messages = fetch_messages("test-exc", db_path=db_path)
            # Should contain exception info in session_end
            assert any("ValueError" in msg.get("message", "") for msg in messages)


class TestFetchMessages:
    """Tests for fetch_messages function."""

    def test_returns_list(self) -> None:
        from codex.logging.session_logger import fetch_messages, init_db

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            init_db(db_path)
            result = fetch_messages("nonexistent", db_path=db_path)
            assert isinstance(result, list)

    def test_returns_logged_messages(self) -> None:
        from codex.logging.session_logger import fetch_messages, log_message

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            log_message("fetch-test", "user", "Hello world", db_path=db_path)

            messages = fetch_messages("fetch-test", db_path=db_path)
            assert len(messages) > 0, "Messages must not be empty"
            assert any("Hello world" in msg.get("message", "") for msg in messages)


class TestMigrateLegacyEvents:
    """Tests for migrate_legacy_events function."""

    def test_backfills_seq_column(self) -> None:
        from codex.logging.session_logger import init_db, migrate_legacy_events

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            init_db(db_path)

            # Insert a row without seq
            conn = sqlite3.connect(db_path)
            conn.execute(
                "INSERT INTO session_events (ts, session_id, role, message) VALUES (?, ?, ?, ?)",
                (time.time(), "legacy-session", "user", "Legacy message"),
            )
            conn.commit()
            conn.close()

            # Run migration
            migrate_legacy_events(db_path)

            # Check seq is now set
            conn = sqlite3.connect(db_path)
            cursor = conn.execute(
                "SELECT seq FROM session_events WHERE session_id = ?", ("legacy-session",)
            )
            rows = cursor.fetchall()
            conn.close()

            assert len(rows) > 0, "Rows must not be empty"
            assert rows[0][0] is not None, "Value must be initialized"


class TestConcurrentAccess:
    """Tests for concurrent database access."""

    def test_concurrent_logging(self) -> None:
        from codex.logging.session_logger import fetch_messages, log_message

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"

            def log_messages(session_id: str, count: int) -> None:
                for i in range(count):
                    log_message(session_id, "user", f"Message {i}", db_path=db_path)

            threads = []
            for i in range(5):
                t = threading.Thread(target=log_messages, args=(f"concurrent-{i}", 10))
                threads.append(t)

            for t in threads:
                t.start()

            for t in threads:
                t.join()

            # Verify messages were logged
            total = 0
            for i in range(5):
                messages = fetch_messages(f"concurrent-{i}", db_path=db_path)
                total += len(messages)

            assert total == 50, "total is not valid"


class TestConnectionPooling:
    """Tests for SQLite connection pooling."""

    def test_pool_environment_variable(self) -> None:
        from codex.logging.session_logger import USE_POOL

        # USE_POOL is determined at import time by CODEX_SQLITE_POOL env var
        assert isinstance(USE_POOL, bool)

    def test_conn_pool_is_dict(self) -> None:
        from codex.logging.session_logger import CONN_POOL

        assert isinstance(CONN_POOL, dict)

    def test_initialized_paths_is_set(self) -> None:
        from codex.logging.session_logger import INITIALIZED_PATHS

        assert isinstance(INITIALIZED_PATHS, set)
