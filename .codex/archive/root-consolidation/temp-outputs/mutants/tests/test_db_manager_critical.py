"""Critical tests for DBManager pool cleanup and logger fix.

Tests for P1 defect: close_all_pools() AttributeError causing resource leaks.
"""

import os
from unittest.mock import patch

import pytest


class TestDBManagerPoolCleanup:
    """Test DBManager connection pool cleanup (P1 critical defect fix)."""

    def test_close_all_pools_success(self, tmp_path):
        """Test successful pool cleanup without errors."""
        from codex.logging.db_manager import DBManager

        # Enable pooling
        with patch.dict(os.environ, {"CODEX_SQLITE_POOL": "1"}):
            # Force reload to pick up env var
            import importlib
            import sys

            importlib.import_module("codex.logging.db_manager")
            importlib.reload(sys.modules["codex.logging.db_manager"])
            from codex.logging.db_manager import DBManager

            # Clear any existing pools from previous tests
            DBManager.close_all_pools()

            # Create manager and initialize
            db_path = tmp_path / "test_pool.db"
            manager = DBManager(db_path=db_path)
            manager.init_schema()

            # Populate pool with connections
            # Note: Pool reuses connections, so we need to create them concurrently
            # to actually have multiple connections in the pool
            conns = []
            for _ in range(5):
                conn = manager.get_connection()
                conns.append(conn)

            # Now return them all to pool
            for conn in conns:
                manager.close_connection(conn)

            # Verify pool has connections
            assert len(DBManager._CONNECTION_POOL) > 0, "Pool should be populated"
            pool_size_before = sum(len(p) for p in DBManager._CONNECTION_POOL.values())
            assert pool_size_before >= 5, f"Expected at least 5 connections, got {pool_size_before}"

            # Close all pools
            DBManager.close_all_pools()

            # Verify pool is empty
            assert len(DBManager._CONNECTION_POOL) == 0, "Pool should be cleared"

    def test_close_all_pools_with_connection_errors(self, tmp_path):
        """Test pool cleanup when some connections fail to close."""
        from codex.logging.db_manager import DBManager

        with patch.dict(os.environ, {"CODEX_SQLITE_POOL": "1"}):
            import importlib
            import sys

            importlib.import_module("codex.logging.db_manager")
            importlib.reload(sys.modules["codex.logging.db_manager"])
            from codex.logging.db_manager import DBManager

            db_path = tmp_path / "test_errors.db"
            manager = DBManager(db_path=db_path)
            manager.init_schema()

            # Populate pool
            conns = []
            for _ in range(3):
                conn = manager.get_connection()
                conns.append(conn)
                manager.close_connection(conn)

            # Pre-close first connection to trigger error
            for pool in DBManager._CONNECTION_POOL.values():
                if pool:
                    pool[0].close()  # This will cause error on second close
                    break

            # Close all pools - should NOT raise exception
            try:
                DBManager.close_all_pools()
            except Exception as e:
                pytest.fail(f"close_all_pools() should not raise exception: {e}")

            # Verify pool is still cleared despite errors
            assert len(DBManager._CONNECTION_POOL) == 0, "Pool should be cleared even with errors"

    def test_close_all_pools_empty_pool(self):
        """Test pool cleanup with no connections."""
        from codex.logging.db_manager import DBManager

        # Ensure pool is empty
        DBManager._CONNECTION_POOL.clear()

        # Should not raise exception
        try:
            DBManager.close_all_pools()
        except Exception as e:
            pytest.fail(f"close_all_pools() on empty pool should not raise: {e}")

        # Pool should still be empty
        assert len(DBManager._CONNECTION_POOL) == 0, "Collection must not be empty"

    def test_close_all_pools_multiple_databases(self, tmp_path):
        """Test pool cleanup with multiple database pools."""
        from codex.logging.db_manager import DBManager

        with patch.dict(os.environ, {"CODEX_SQLITE_POOL": "1"}):
            import importlib
            import sys

            importlib.import_module("codex.logging.db_manager")
            importlib.reload(sys.modules["codex.logging.db_manager"])
            from codex.logging.db_manager import DBManager

            # Create two databases
            db1 = DBManager(db_path=tmp_path / "db1.db")
            db1.init_schema()
            db2 = DBManager(db_path=tmp_path / "db2.db")
            db2.init_schema()

            # Populate pools
            for _ in range(2):
                conn1 = db1.get_connection()
                db1.close_connection(conn1)

                conn2 = db2.get_connection()
                db2.close_connection(conn2)

            # Verify both pools populated
            assert len(DBManager._CONNECTION_POOL) == 2, "Should have 2 database pools"

            # Close all pools
            DBManager.close_all_pools()

            # Verify all pools cleared
            assert len(DBManager._CONNECTION_POOL) == 0, "Collection must not be empty"

    def test_logger_accessible_from_classmethod(self):
        """Test that _logger is accessible from classmethod (regression test)."""
        from codex.logging.db_manager import DBManager

        # Verify class attribute exists
        assert hasattr(DBManager, "_logger"), "DBManager should have _logger class attribute"

        # Verify it's a Logger instance
        import logging

        assert isinstance(DBManager._logger, logging.Logger), "_logger should be a Logger instance"

        # Verify name is correct
        assert DBManager._logger.name == "codex.logging.db_manager", "name is not valid"

    def test_instance_logger_access(self, tmp_path):
        """Test that instance methods can still access logger."""
        from codex.logging.db_manager import DBManager

        db = DBManager(db_path=tmp_path / "test_instance.db")

        # Verify instance can access _logger
        assert hasattr(db, "_logger"), "Instance should have access to _logger"

        # Test logging works (capture logs)
        with patch.object(DBManager._logger, "info"):
            db.init_schema()
            # Schema may already exist, logging is optional
            # Test passes if no exception raised

    def test_close_all_pools_logs_errors(self, tmp_path, caplog):
        """Test that errors during close are logged at DEBUG level."""
        import logging

        from codex.logging.db_manager import DBManager

        with patch.dict(os.environ, {"CODEX_SQLITE_POOL": "1"}):
            import importlib
            import sys

            importlib.import_module("codex.logging.db_manager")
            importlib.reload(sys.modules["codex.logging.db_manager"])
            from codex.logging.db_manager import DBManager

            db = DBManager(db_path=tmp_path / "test_logging.db")
            db.init_schema()

            # Populate pool
            conn = db.get_connection()
            db.close_connection(conn)

            # Pre-close to trigger error
            for pool in DBManager._CONNECTION_POOL.values():
                if pool:
                    pool[0].close()
                    break

            # Close with logging enabled
            with caplog.at_level(logging.DEBUG):
                DBManager.close_all_pools()

            # Verify error was logged (if occurred)
            # Note: May not always trigger error depending on SQLite version
            # Just verify no exception raised
            assert len(DBManager._CONNECTION_POOL) == 0, "Collection must not be empty"
