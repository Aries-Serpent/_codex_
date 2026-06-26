"""Tests for codex.db.sqlite_patch module.

Phase 6 tests covering:
- PooledConnectionProxy class
- Connection pooling functions
- Pragma application
- Auto-enable from environment
"""

from __future__ import annotations

import importlib
import os
import sqlite3
import threading
from unittest.mock import MagicMock

import pytest


def test_import_module():
    """Test module can be imported."""
    module = "codex.db.sqlite_patch"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")


class TestPooledConnectionProxy:
    """Tests for PooledConnectionProxy class."""

    @pytest.fixture
    def mock_connection(self):
        """Create a mock SQLite connection."""
        return MagicMock(spec=sqlite3.Connection)

    @pytest.fixture
    def proxy(self, mock_connection):
        """Create a PooledConnectionProxy instance."""
        from codex.db.sqlite_patch import PooledConnectionProxy

        key = ("test.db", os.getpid(), threading.get_ident(), "session1")
        return PooledConnectionProxy(mock_connection, key)

    def test_proxy_creation(self, proxy, mock_connection):
        """Test proxy can be created."""
        assert proxy._conn == mock_connection, "_conn is not valid"

    def test_proxy_getattr_delegates(self, proxy, mock_connection):
        """Test that attribute access delegates to connection."""
        mock_connection.cursor = MagicMock(return_value="cursor")
        result = proxy.cursor
        assert result == mock_connection.cursor, "Result must not be empty"

    def test_proxy_row_factory_access(self, proxy, mock_connection):
        """Test accessing row_factory through proxy."""
        mock_connection.row_factory = sqlite3.Row
        assert proxy.row_factory == mock_connection.row_factory, "row_factory is not valid"


class TestKeyGeneration:
    """Tests for _key function."""

    @pytest.fixture
    def key_func(self):
        """Import _key function."""
        from codex.db.sqlite_patch import _key

        return _key

    @pytest.fixture
    def clean_env(self):
        """Clear session env var for testing."""
        saved = os.environ.pop("CODEX_SESSION_ID", None)
        yield
        if saved:
            os.environ["CODEX_SESSION_ID"] = saved

    def test_key_returns_tuple(self, key_func, clean_env):
        """Test _key returns a tuple."""
        result = key_func("test.db")
        assert isinstance(result, tuple)
        assert len(result) == 4, "Result must not be empty"

    def test_key_includes_database_path(self, key_func, clean_env):
        """Test key includes database path."""
        result = key_func("test.db")
        assert result[0] == "test.db", "Result must not be empty"

    def test_key_includes_process_id(self, key_func, clean_env):
        """Test key includes process ID."""
        result = key_func("test.db")
        assert result[1] == os.getpid(), "Result must not be empty"

    def test_key_includes_thread_id(self, key_func, clean_env):
        """Test key includes thread ID."""
        result = key_func("test.db")
        assert result[2] == threading.get_ident(), "Result must not be empty"

    def test_key_includes_session_id(self, key_func, clean_env):
        """Test key includes session ID."""
        os.environ["CODEX_SESSION_ID"] = "test-session"
        result = key_func("test.db")
        assert result[3] == "test-session", "Result must not be empty"

    def test_key_empty_session_when_not_set(self, key_func, clean_env):
        """Test key has empty session when not set."""
        result = key_func("test.db")
        assert result[3] == "", "Result must not be empty"


class TestApplyPragmas:
    """Tests for _apply_pragmas function."""

    @pytest.fixture
    def apply_pragmas(self):
        """Import _apply_pragmas function."""
        from codex.db.sqlite_patch import _apply_pragmas

        return _apply_pragmas

    def test_apply_pragmas_executes_wal(self, apply_pragmas, tmp_path):
        """Test that WAL pragma is applied."""
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))

        apply_pragmas(conn)

        # Verify WAL mode was set
        cursor = conn.execute("PRAGMA journal_mode;")
        result = cursor.fetchone()[0]
        assert result.upper() == "WAL", "Result must not be empty"

        conn.close()

    def test_apply_pragmas_handles_error(self, apply_pragmas):
        """Test that pragma errors are logged, not raised."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = sqlite3.Error("test error")
        mock_conn.cursor.return_value = mock_cursor

        # Should not raise
        apply_pragmas(mock_conn)


class TestPooledConnect:
    """Tests for pooled_connect function."""

    @pytest.fixture
    def clean_env(self):
        """Clear pooling env var for testing."""
        saved = os.environ.pop("CODEX_SQLITE_POOL", None)
        yield
        if saved:
            os.environ["CODEX_SQLITE_POOL"] = saved

    @pytest.fixture
    def pooled_connect(self):
        """Import pooled_connect function."""
        from codex.db.sqlite_patch import pooled_connect

        return pooled_connect

    def test_pooled_connect_without_pooling_enabled(self, pooled_connect, tmp_path, clean_env):
        """Test pooled_connect falls back to original when pooling disabled."""
        os.environ["CODEX_SQLITE_POOL"] = "0"
        db_path = str(tmp_path / "test.db")

        conn = pooled_connect(db_path)

        # Should return regular connection, not proxy
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_pooled_connect_with_pooling_enabled(self, pooled_connect, tmp_path, clean_env):
        """Test pooled_connect returns proxy when pooling enabled."""
        from codex.db.sqlite_patch import PooledConnectionProxy, _close_all

        os.environ["CODEX_SQLITE_POOL"] = "1"
        db_path = str(tmp_path / "test.db")

        try:
            conn = pooled_connect(db_path)
            assert isinstance(conn, PooledConnectionProxy)
        finally:
            _close_all()  # Clean up pooled connections

    def test_pooled_connect_reuses_connection(self, pooled_connect, tmp_path, clean_env):
        """Test that pooled_connect reuses connections."""
        from codex.db.sqlite_patch import _CONN_POOL, _POOL_LOCK, _close_all

        os.environ["CODEX_SQLITE_POOL"] = "1"
        db_path = str(tmp_path / "test.db")

        try:
            # Clear pool first under lock
            with _POOL_LOCK:
                _CONN_POOL.clear()

            conn1 = pooled_connect(db_path)
            conn2 = pooled_connect(db_path)

            # Should be same underlying connection
            assert conn1._conn is conn2._conn, "_conn is not valid"
        finally:
            _close_all()  # Clean up pooled connections


class TestEnableDisablePooling:
    """Tests for enable_pooling and disable_pooling functions."""

    @pytest.fixture
    def save_connect(self):
        """Save original connect and restore after test."""
        original = sqlite3.connect
        yield
        sqlite3.connect = original

    def test_enable_pooling(self, save_connect):
        """Test enable_pooling replaces sqlite3.connect."""
        from codex.db.sqlite_patch import enable_pooling, pooled_connect

        enable_pooling()

        assert sqlite3.connect == pooled_connect, "connect is not valid"

    def test_disable_pooling(self, save_connect):
        """Test disable_pooling restores original connect."""
        from codex.db.sqlite_patch import _ORIG_CONNECT, disable_pooling, enable_pooling

        enable_pooling()
        disable_pooling()

        assert sqlite3.connect == _ORIG_CONNECT, "connect is not valid"


class TestAutoEnableFromEnv:
    """Tests for auto_enable_from_env function."""

    @pytest.fixture
    def clean_env(self):
        """Clear pooling env var for testing."""
        saved = os.environ.pop("CODEX_SQLITE_POOL", None)
        yield
        if saved:
            os.environ["CODEX_SQLITE_POOL"] = saved

    @pytest.fixture
    def save_connect(self):
        """Save original connect and restore after test."""
        original = sqlite3.connect
        yield
        sqlite3.connect = original

    def test_auto_enable_when_env_set_to_1(self, clean_env, save_connect):
        """Test auto enable when CODEX_SQLITE_POOL=1."""
        from codex.db.sqlite_patch import auto_enable_from_env, pooled_connect

        os.environ["CODEX_SQLITE_POOL"] = "1"

        auto_enable_from_env()

        assert sqlite3.connect == pooled_connect, "connect is not valid"

    def test_auto_enable_when_env_set_to_true(self, clean_env, save_connect):
        """Test auto enable when CODEX_SQLITE_POOL=true."""
        from codex.db.sqlite_patch import auto_enable_from_env, pooled_connect

        os.environ["CODEX_SQLITE_POOL"] = "true"

        auto_enable_from_env()

        assert sqlite3.connect == pooled_connect, "connect is not valid"

    def test_no_enable_when_env_not_set(self, clean_env, save_connect):
        """Test no enable when env var not set."""
        from codex.db.sqlite_patch import _ORIG_CONNECT, auto_enable_from_env

        auto_enable_from_env()

        # Should still be original
        assert sqlite3.connect == _ORIG_CONNECT, "connect is not valid"


class TestCloseAll:
    """Tests for _close_all cleanup function."""

    def test_close_all_clears_pool(self, tmp_path):
        """Test that _close_all clears the connection pool."""
        from codex.db.sqlite_patch import _CONN_POOL, _close_all

        # Add a connection to pool
        db_path = str(tmp_path / "test.db")
        conn = sqlite3.connect(db_path)
        key = (db_path, os.getpid(), threading.get_ident(), "")
        _CONN_POOL[key] = conn

        _close_all()

        assert len(_CONN_POOL) == 0, "_conn_pool must not be empty"
