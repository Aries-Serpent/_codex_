"""
Test Db Manager

Comprehensive test module for DBManager class in codex.logging.db_manager.
"""

from __future__ import annotations

import importlib
import sqlite3
import tempfile
import threading
from pathlib import Path

import pytest


class TestDBManagerImports:
    """Tests for db_manager module imports."""

    def test_import_module(self) -> None:
        module = "codex.logging.db_manager"
        try:
            importlib.import_module(module)
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_import_db_manager_class(self) -> None:
        from codex.logging.db_manager import DBManager

        assert DBManager is not None, "DBManager must be initialized"

    def test_import_db_manager_singleton(self) -> None:
        from codex.logging.db_manager import db_manager

        assert db_manager is not None, "db_manager must be initialized"


class TestDBManagerInitialization:
    """Tests for DBManager initialization."""

    def test_init_with_default_path(self) -> None:
        from codex.logging.db_manager import DBManager

        dm = DBManager()
        assert dm.db_path is not None, "db_path must be initialized"

    def test_init_with_custom_path(self) -> None:
        from codex.logging.db_manager import DBManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dm = DBManager(db_path=db_path)
            assert dm.db_path == db_path, "db_path is not valid"

    def test_init_creates_parent_directory(self) -> None:
        from codex.logging.db_manager import DBManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "subdir" / "test.db"
            dm = DBManager(db_path=db_path)
            dm.init_schema()
            assert db_path.parent.exists(), "Condition must be true"


class TestDBManagerSchema:
    """Tests for schema initialization."""

    def test_init_schema(self) -> None:
        from codex.logging.db_manager import DBManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dm = DBManager(db_path=db_path)
            dm.init_schema()
            assert db_path.exists(), "Condition must be true"

    def test_init_schema_creates_session_events_table(self) -> None:
        from codex.logging.db_manager import DBManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dm = DBManager(db_path=db_path)
            dm.init_schema()

            conn = sqlite3.connect(db_path)
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='session_events'"
            )
            tables = cursor.fetchall()
            conn.close()

            assert len(tables) == 1, "Tables must not be empty"

    def test_init_schema_idempotent(self) -> None:
        from codex.logging.db_manager import DBManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dm = DBManager(db_path=db_path)
            dm.init_schema()
            dm.init_schema()  # Second call should not raise
            assert db_path.exists(), "Condition must be true"


class TestDBManagerConnection:
    """Tests for connection management."""

    def test_get_connection(self) -> None:
        from codex.logging.db_manager import DBManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dm = DBManager(db_path=db_path)
            dm.init_schema()

            conn = dm.get_connection()
            assert conn is not None, "conn must be initialized"
            # Connection may be a proxy when pooling is enabled
            assert hasattr(conn, "execute")
            dm.close_connection(conn)

    def test_connection_context_manager(self) -> None:
        from codex.logging.db_manager import DBManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dm = DBManager(db_path=db_path)
            dm.init_schema()

            with dm.connection() as conn:
                assert conn is not None, "conn must be initialized"
                # Connection may be a proxy when pooling is enabled
                assert hasattr(conn, "execute")

    def test_close_connection(self) -> None:
        from codex.logging.db_manager import DBManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dm = DBManager(db_path=db_path)
            dm.init_schema()

            conn = dm.get_connection()
            dm.close_connection(conn)
            # Should not raise even if called twice
            dm.close_connection(conn)


class TestDBManagerPooling:
    """Tests for connection pooling."""

    def test_pool_enabled_class_attribute(self) -> None:
        from codex.logging.db_manager import DBManager

        assert isinstance(DBManager._POOL_ENABLED, bool)

    def test_connection_pool_class_attribute(self) -> None:
        from codex.logging.db_manager import DBManager

        assert isinstance(DBManager._CONNECTION_POOL, dict)

    def test_close_all_pools(self) -> None:
        from codex.logging.db_manager import DBManager

        # Should not raise even if no pools exist
        DBManager.close_all_pools()


class TestDBManagerThreadSafety:
    """Tests for thread safety."""

    def test_concurrent_init_schema(self) -> None:
        from codex.logging.db_manager import DBManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dm = DBManager(db_path=db_path)

            errors = []

            def init_thread():
                try:
                    dm.init_schema()
                except (IOError, OSError) as e:
                    errors.append(e)

            threads = [threading.Thread(target=init_thread) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(errors) == 0, "Errors must not be empty"
            assert db_path.exists(), "Condition must be true"

    def test_concurrent_connections(self) -> None:
        from codex.logging.db_manager import DBManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            dm = DBManager(db_path=db_path)
            dm.init_schema()

            errors = []

            def connect_thread():
                try:
                    with dm.connection() as conn:
                        conn.execute("SELECT 1")
                except (ConnectionError, TimeoutError) as e:
                    errors.append(e)

            threads = [threading.Thread(target=connect_thread) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(errors) == 0, "Errors must not be empty"


class TestDBManagerSingleton:
    """Tests for singleton db_manager instance."""

    def test_singleton_exists(self) -> None:
        from codex.logging.db_manager import db_manager

        assert db_manager is not None, "db_manager must be initialized"

    def test_singleton_is_db_manager(self) -> None:
        from codex.logging.db_manager import DBManager, db_manager

        assert isinstance(db_manager, DBManager)


class TestDBManagerClassAttributes:
    """Tests for class-level attributes."""

    def test_init_lock_exists(self) -> None:
        from codex.logging.db_manager import DBManager

        assert hasattr(DBManager, "_INIT_LOCK")

    def test_initialized_dbs_exists(self) -> None:
        from codex.logging.db_manager import DBManager

        assert hasattr(DBManager, "_INITIALIZED_DBS")
        assert isinstance(DBManager._INITIALIZED_DBS, set)

    def test_pool_lock_exists(self) -> None:
        from codex.logging.db_manager import DBManager

        assert hasattr(DBManager, "_POOL_LOCK")

    def test_logger_exists(self) -> None:
        from codex.logging.db_manager import DBManager

        assert hasattr(DBManager, "_logger")
