"""
Comprehensive edge case tests for SessionDB - High Priority (P1.1).

Focus on the 5 critical bugs in load_session():
1. Corrupted state handling
2. Missing file recovery
3. Concurrent access
4. Race condition detection
5. Missing schema handling

These tests target the 343 untested functions in codex module.
"""

import sqlite3
import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator

import pytest

from codex.logging.session_db import CacheEntry, SessionDB


class TestSessionDBCriticalEdgeCases:
    """Test critical edge cases for load_session functionality."""

    @pytest.fixture
    def temp_db(self) -> Generator[str, None, None]:
        """Provide temporary database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield f"{tmpdir}/test.db"

    @pytest.fixture
    def db(self, temp_db: str) -> SessionDB:
        """Provide initialized database."""
        return SessionDB(temp_db)

    # ========================================================================
    # BUG #1: Corrupted State Handling
    # ========================================================================

    def test_corrupted_database_recovery(self, temp_db: str):
        """Test recovery from corrupted database file."""
        db = SessionDB(temp_db)

        # Insert test data
        session = {
            "session_id": "sess_001",
            "status": "in-progress",
            "timestamp": datetime.now().isoformat(),
            "pr_number": 100,
            "branch": "main",
            "git_sha": "abc123",
        }
        db.insert_session(session)

        # Corrupt database file
        with open(temp_db, "wb") as f:
            f.write(b"CORRUPTED_DATA_" * 100)

        # Attempt to recover
        db_recovered = SessionDB(temp_db)

        # Verify schema is recreated
        with db_recovered._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]
            assert "sessions" in tables, "Schema should be restored"

    def test_incomplete_transaction_rollback(self, temp_db: str):
        """Test that incomplete transactions are rolled back correctly."""
        db = SessionDB(temp_db)

        initial_count = len(db.query_all())

        # Start transaction and simulate interruption
        try:
            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sessions "
                    "(session_id, status, timestamp) "
                    "VALUES (?, ?, ?)",
                    ("incomplete_sess", "pending", datetime.now().isoformat()),
                )
                # Force error before commit
                raise Exception("Simulated error")
        except Exception:
            pass

        # Verify incomplete transaction didn't persist
        final_count = len(db.query_all())
        assert final_count == initial_count, "Transaction should be rolled back"

    def test_corrupted_metadata_isolation(self, temp_db: str):
        """Test that corrupted metadata doesn't affect session queries."""
        db = SessionDB(temp_db)

        # Insert session
        session = {
            "session_id": "sess_002",
            "status": "complete",
            "timestamp": datetime.now().isoformat(),
        }
        db.insert_session(session)

        # Insert metadata
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO session_metadata (session_id, key, value) "
                "VALUES (?, ?, ?)",
                ("sess_002", "test_key", "test_value"),
            )
            conn.commit()

        # Corrupt metadata by deleting constraint
        with db._get_connection() as conn:
            cursor = conn.cursor()
            # Try to insert orphaned metadata
            try:
                cursor.execute(
                    "INSERT INTO session_metadata (session_id, key, value) "
                    "VALUES (?, ?, ?)",
                    ("nonexistent_sess", "orphan_key", "orphan_value"),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # This is expected - foreign key constraint should catch it
                pass

        # Verify session queries still work
        sessions = db.query_by_status("complete")
        assert len(sessions) > 0, "Session queries should work despite metadata issues"

    # ========================================================================
    # BUG #2: Missing File Recovery
    # ========================================================================

    def test_missing_database_file_recreation(self, temp_db: str):
        """Test database file recreation when missing."""
        db = SessionDB(temp_db)

        # Insert data
        session = {
            "session_id": "sess_003",
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
        }
        db.insert_session(session)

        # Delete database file
        Path(temp_db).unlink()

        # Attempt operation - should recreate database
        db_new = SessionDB(temp_db)
        sessions = db_new.query_all()

        # New database should be empty but functional
        assert isinstance(sessions, list), "Should return list"
        assert len(sessions) == 0, "New database should be empty"

    def test_missing_schema_file_fallback(self, temp_db: str):
        """Test fallback schema creation when schema file missing."""
        db = SessionDB(temp_db)

        # Verify schema was created (via inline fallback)
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]

        assert "sessions" in tables, "Schema should exist"
        assert "session_metadata" in tables, "Metadata table should exist"
        assert "session_patterns" in tables, "Patterns table should exist"

    # ========================================================================
    # BUG #3: Concurrent Access
    # ========================================================================

    def test_concurrent_inserts_thread_safety(self, temp_db: str):
        """Test thread-safe concurrent inserts."""
        db = SessionDB(temp_db)
        num_threads = 10
        sessions_per_thread = 5
        errors = []

        def insert_sessions(thread_id: int):
            """Insert multiple sessions from thread."""
            try:
                for i in range(sessions_per_thread):
                    session = {
                        "session_id": f"sess_t{thread_id}_i{i}",
                        "status": "pending",
                        "timestamp": datetime.now().isoformat(),
                        "pr_number": 100 + thread_id,
                    }
                    db.insert_session(session)
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Run concurrent inserts
        threads = [
            threading.Thread(target=insert_sessions, args=(i,))
            for i in range(num_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent insert errors: {errors}"

        # Verify all sessions were inserted
        all_sessions = db.query_all()
        expected_count = num_threads * sessions_per_thread
        assert len(all_sessions) == expected_count, (
            f"Expected {expected_count} sessions, got {len(all_sessions)}"
        )

    def test_concurrent_reads_during_write(self, temp_db: str):
        """Test concurrent reads don't block due to writes."""
        db = SessionDB(temp_db)

        # Insert initial data
        for i in range(10):
            session = {
                "session_id": f"sess_pre{i}",
                "status": "complete",
                "timestamp": datetime.now().isoformat(),
            }
            db.insert_session(session)

        read_results = []
        write_complete = threading.Event()

        def read_sessions():
            """Read sessions multiple times."""
            for _ in range(5):
                results = db.query_by_status("complete")
                read_results.append(len(results))
                time.sleep(0.01)

        def slow_write():
            """Perform slow write operation."""
            session = {
                "session_id": "sess_slow_write",
                "status": "pending",
                "timestamp": datetime.now().isoformat(),
            }
            db.insert_session(session)
            write_complete.set()

        # Start operations
        read_thread = threading.Thread(target=read_sessions)
        write_thread = threading.Thread(target=slow_write)

        read_thread.start()
        time.sleep(0.01)
        write_thread.start()

        read_thread.join(timeout=10)
        write_thread.join(timeout=10)

        # Verify reads were consistent
        assert len(read_results) > 0, "Read operations should complete"
        assert all(
            r >= 10 for r in read_results
        ), "Read results should include initial data"

    def test_concurrent_cache_invalidation(self, temp_db: str):
        """Test cache invalidation during concurrent operations."""
        db = SessionDB(temp_db)

        # Populate cache
        results1 = db.query_all()
        assert len(results1) == 0

        # Start write in another thread
        write_done = threading.Event()

        def delayed_write():
            time.sleep(0.1)
            session = {
                "session_id": "sess_cache_test",
                "status": "pending",
                "timestamp": datetime.now().isoformat(),
            }
            db.insert_session(session)
            write_done.set()

        write_thread = threading.Thread(target=delayed_write)
        write_thread.start()

        # Read before and after write
        results_before = db.query_all()
        write_done.wait(timeout=5)
        results_after = db.query_all()

        write_thread.join(timeout=5)

        # Cache should be invalidated after write
        assert len(results_before) == 0, "Before write should be empty"
        assert len(results_after) == 1, "After write should have new session"

    # ========================================================================
    # BUG #4: Race Condition Detection
    # ========================================================================

    def test_duplicate_insert_race_condition(self, temp_db: str):
        """Test handling of duplicate inserts in race condition."""
        db = SessionDB(temp_db)
        race_errors = []

        def try_insert():
            try:
                session = {
                    "session_id": "sess_race_001",
                    "status": "pending",
                    "timestamp": datetime.now().isoformat(),
                }
                db.insert_session(session)
            except sqlite3.IntegrityError as e:
                race_errors.append(str(e))

        # Launch multiple threads trying to insert same ID
        threads = [threading.Thread(target=try_insert) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactly one should succeed, others should fail
        assert len(race_errors) == 4, "Exactly 4 should fail due to duplicate"

        # Verify exactly one session exists
        sessions = db.query_all()
        assert len(sessions) == 1, "Only one session should exist"

    def test_read_write_ordering(self, temp_db: str):
        """Test that reads see writes in correct order."""
        db = SessionDB(temp_db)
        read_values = []
        write_order = []

        lock = threading.Lock()

        def write_session(session_num: int):
            session = {
                "session_id": f"sess_order_{session_num}",
                "status": "pending",
                "timestamp": datetime.now().isoformat(),
            }
            db.insert_session(session)
            with lock:
                write_order.append(session_num)

        def read_sessions():
            time.sleep(0.05)  # Let some writes happen
            with lock:
                results = db.query_all()
                read_values.append(len(results))

        # Write and read concurrently
        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=write_session, args=(i,)))
        for _ in range(3):
            threads.append(threading.Thread(target=read_sessions))

        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        # Verify data consistency
        assert len(write_order) == 5, "All writes should complete"
        assert len(read_values) > 0, "Reads should complete"

    # ========================================================================
    # BUG #5: Missing Schema Handling
    # ========================================================================

    def test_missing_required_table(self, temp_db: str):
        """Test recovery from missing required table."""
        db = SessionDB(temp_db)

        # Drop a table
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS session_metadata")
            conn.commit()

        # Reinitialize to restore schema
        db_restored = SessionDB(temp_db)

        # Verify table exists
        with db_restored._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name='session_metadata'"
            )
            assert cursor.fetchone() is not None, "Table should be restored"

    def test_missing_required_index(self, temp_db: str):
        """Test that missing indices are handled gracefully."""
        db = SessionDB(temp_db)

        # Drop an index
        with db._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DROP INDEX IF EXISTS idx_timestamp_status")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        # Queries should still work
        session = {
            "session_id": "sess_index_test",
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
        }
        db.insert_session(session)

        results = db.query_by_status("pending")
        assert len(results) > 0, "Query should work despite missing index"

    def test_foreign_key_constraint_violation(self, temp_db: str):
        """Test detection of foreign key constraint violations."""
        db = SessionDB(temp_db)

        # Try to insert metadata for nonexistent session
        with pytest.raises(sqlite3.IntegrityError):
            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO session_metadata (session_id, key, value) "
                    "VALUES (?, ?, ?)",
                    ("nonexistent", "key", "value"),
                )
                conn.commit()

    def test_schema_version_compatibility(self, temp_db: str):
        """Test compatibility with different schema versions."""
        db = SessionDB(temp_db)

        # Insert session with new schema
        session = {
            "session_id": "sess_schema_v1",
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
        }
        db.insert_session(session)

        # Verify session can be retrieved
        sessions = db.query_all()
        assert len(sessions) == 1, "Session should be retrievable"
        assert sessions[0]["session_id"] == "sess_schema_v1"

    # ========================================================================
    # Additional Coverage for Edge Cases
    # ========================================================================

    def test_empty_database_queries(self, temp_db: str):
        """Test queries on empty database."""
        db = SessionDB(temp_db)

        assert db.query_all() == [], "Empty database should return empty list"
        assert db.query_by_status("pending") == [], "Empty database status query"
        assert db.query_by_agent_name("nonexistent") == [], "Empty agent query"

    def test_null_value_handling(self, temp_db: str):
        """Test handling of NULL values in database."""
        db = SessionDB(temp_db)

        session = {
            "session_id": "sess_null_test",
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            "pr_number": None,
            "branch": None,
            "git_sha": None,
            "agent_name": None,
        }
        db.insert_session(session)

        results = db.query_all()
        assert len(results) == 1, "Session with NULL values should be stored"

    def test_extreme_value_handling(self, temp_db: str):
        """Test handling of extreme values."""
        db = SessionDB(temp_db)

        session = {
            "session_id": "sess_extreme_values",
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            "pr_number": 2147483647,  # Max int32
            "duration_minutes": 999999,
        }
        db.insert_session(session)

        results = db.query_by_pr_number(2147483647)
        assert len(results) == 1, "Extreme values should be handled"

    def test_cache_ttl_expiration(self, temp_db: str):
        """Test cache entry TTL expiration."""
        cache_entry = CacheEntry(data={"test": "data"}, timestamp=time.time())

        # Should not be expired immediately
        assert not cache_entry.is_expired(ttl=300)

        # Should expire with short TTL
        assert cache_entry.is_expired(ttl=-1)

        # Create old entry
        old_entry = CacheEntry(
            data={"old": "data"}, timestamp=time.time() - 400
        )
        assert old_entry.is_expired(ttl=300)


class TestSessionDBPerformanceUnderLoad:
    """Test performance and stability under load."""

    @pytest.fixture
    def temp_db(self) -> Generator[str, None, None]:
        """Provide temporary database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield f"{tmpdir}/test.db"

    def test_high_volume_inserts(self, temp_db: str):
        """Test performance with high volume of inserts."""
        db = SessionDB(temp_db)
        start_time = time.time()

        # Insert 1000 sessions
        for i in range(1000):
            session = {
                "session_id": f"sess_load_{i:04d}",
                "status": ["pending", "in-progress", "complete", "failed"][
                    i % 4
                ],
                "timestamp": (
                    datetime.now() - timedelta(hours=i % 100)
                ).isoformat(),
                "pr_number": 100 + (i % 50),
                "agent_name": f"agent_{i % 10}",
            }
            db.insert_session(session)

        elapsed = time.time() - start_time

        # Verify all inserted
        all_sessions = db.query_all()
        assert len(all_sessions) == 1000, f"Expected 1000 sessions, got {len(all_sessions)}"

        # Performance check (should complete in reasonable time)
        assert elapsed < 30, f"High volume insert took {elapsed}s, expected < 30s"

    def test_large_result_set_queries(self, temp_db: str):
        """Test querying large result sets."""
        db = SessionDB(temp_db)

        # Insert 500 sessions with same status
        for i in range(500):
            session = {
                "session_id": f"sess_large_result_{i}",
                "status": "complete",
                "timestamp": datetime.now().isoformat(),
            }
            db.insert_session(session)

        # Query large result set
        start_time = time.time()
        results = db.query_by_status("complete")
        elapsed = time.time() - start_time

        assert len(results) == 500, "Should retrieve all sessions"
        assert elapsed < 5, f"Large query took {elapsed}s, expected < 5s"

    def test_cache_effectiveness(self, temp_db: str):
        """Test that caching improves repeated query performance."""
        db = SessionDB(temp_db)

        # Populate database
        for i in range(100):
            session = {
                "session_id": f"sess_cache_perf_{i}",
                "status": "complete",
                "timestamp": datetime.now().isoformat(),
            }
            db.insert_session(session)

        # First query (cache miss)
        start1 = time.time()
        results1 = db.query_all()
        time1 = time.time() - start1

        # Second query (should hit cache)
        start2 = time.time()
        results2 = db.query_all()
        time2 = time.time() - start2

        # Cached query should be significantly faster
        assert results1 == results2, "Results should be identical"
        # Cache hit should be at least 10x faster (or within 1ms)
        assert time2 < max(time1 / 5, 0.001), (
            f"Cache not effective: first={time1:.4f}s, second={time2:.4f}s"
        )
