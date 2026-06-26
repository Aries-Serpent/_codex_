"""Advanced connection pooling tests using fixtures.

Tests advanced pooling scenarios:
- Multiple connections
- Concurrent access
- Pool size limits
- Stale connection handling
"""

import threading

import pytest


class TestPoolingBehavior:
    """Test connection pooling behavior with fixtures."""

    @pytest.mark.pool_disable_reuse
    def test_multiple_connections_pooled(self, pooling_db_manager, pool_state_tracker):
        """Test that multiple connections are correctly pooled."""
        # Get and return 3 connections
        for i in range(3):
            conn = pooling_db_manager.get_connection()
            pooling_db_manager.close_connection(conn)

        # Pool should have 3 connections
        pool_state_tracker["assert_pool_size"](3)

    def test_connection_reuse_from_pool(self, pooling_db_manager):
        """Test that connections are reused from pool."""
        # Get first connection
        conn1 = pooling_db_manager.get_connection()
        conn1_id = id(conn1)
        pooling_db_manager.close_connection(conn1)

        # Get second connection (should be same object)
        conn2 = pooling_db_manager.get_connection()
        conn2_id = id(conn2)

        # Should be the same connection object (reused from pool)
        assert conn1_id == conn2_id, "Connection should be reused from pool"

        pooling_db_manager.close_connection(conn2)

    def test_pool_survives_errors(self, pooling_db_manager, pool_state_tracker):
        """Test that pool remains valid after connection errors."""
        # Get connection
        conn = pooling_db_manager.get_connection()

        # Cause an error (invalid SQL)
        try:
            conn.execute("INVALID SQL SYNTAX")
        except Exception as _err:
            _ = None  # Expected error

        # Return connection to pool
        pooling_db_manager.close_connection(conn)

        # Pool should still have the connection
        pool_state_tracker["assert_pool_size"](1)

        # Should be able to get a working connection
        conn2 = pooling_db_manager.get_connection()
        cursor = conn2.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1, "curs is not valid"
        pooling_db_manager.close_connection(conn2)

    def test_concurrent_pool_access(self, pooling_db_manager):
        """Test concurrent access to connection pool."""
        from queue import Queue

        errors = []
        connections_used = Queue()  # Thread-safe queue

        def worker(thread_id):
            try:
                for i in range(5):
                    conn = pooling_db_manager.get_connection()
                    connections_used.put(id(conn))  # Thread-safe put

                    # Use connection
                    cursor = conn.execute("SELECT ?", (thread_id,))
                    result = cursor.fetchone()[0]
                    assert result == thread_id, "Result must not be empty"

                    # Return to pool
                    pooling_db_manager.close_connection(conn)
            except (IOError, OSError) as e:
                errors.append((thread_id, str(e)))

        # Spawn 3 threads
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0, f"Concurrent access errors: {errors}"

        # Verify connections were reused
        connection_ids = []
        while not connections_used.empty():
            connection_ids.append(connections_used.get())

        unique_connections = len(set(connection_ids))
        total_uses = len(connection_ids)

        # Should have reused connections (fewer unique than total uses)
        assert (unique_connections < total_uses), f"Expected connection reuse (unique: {unique_connections}, uses: {total_uses})"


class TestPoolingDisabled:
    """Test behavior when pooling is disabled."""

    def test_no_pooling_when_disabled(self, tmp_path, clean_connection_pool):
        """Test that connections are NOT pooled when pooling disabled."""
        # Import with pooling disabled (default)
        import importlib

        import codex.logging.db_manager

        importlib.reload(codex.logging.db_manager)
        from codex.logging.db_manager import DBManager

        # Verify pooling is disabled
        assert DBManager._POOL_ENABLED is False, "Pooling should be disabled by default"

        db = DBManager(db_path=tmp_path / "no_pool.db")
        db.init_schema()

        # Get and close connection
        conn = db.get_connection()
        db.close_connection(conn)

        # Pool should be empty (connection was closed, not pooled)
        pool_size = sum(len(pool) for pool in DBManager._CONNECTION_POOL.values())
        assert pool_size == 0, f"Pool should be empty when pooling disabled (size: {pool_size})"


class TestPoolingParametrized:
    """Test pooling with parametrization for both modes."""

    def test_basic_operations_both_modes(self, pooling_mode, tmp_path):
        """Test basic operations work with pooling enabled and disabled.

        This test runs twice automatically via pooling_mode fixture:
        - Once with pooling enabled
        - Once with pooling disabled
        """
        from codex.logging.db_manager import DBManager

        db = DBManager(db_path=tmp_path / f"test_{pooling_mode}.db")
        db.init_schema()

        # Basic operations should work regardless of pooling
        conn = db.get_connection()
        cursor = conn.execute("SELECT 1")
        result = cursor.fetchone()[0]
        assert result == 1, "Result must not be empty"

        db.close_connection(conn)

        # Verify expected pool behavior
        pool_size = sum(len(pool) for pool in DBManager._CONNECTION_POOL.values())
        if pooling_mode:
            assert pool_size == 1, "Connection should be in pool when pooling enabled"
        else:
            assert pool_size == 0, "Connection should NOT be in pool when pooling disabled"
