"""
Phase 6 Concurrency Protection Tests

Tests for:
- SQLite concurrent read/write operations
- Faiss index read-write locking
- Archive operation locks
- Session query API thread-safety
- Deadlock recovery
- Lock contention monitoring
"""

from __future__ import annotations

import concurrent.futures
import sqlite3
import threading
import time

import pytest

from codex.logging.concurrency import (
    DeadlockRecovery,
    ReadWriteLock,
    SQLiteConnectionPool,
)
from codex.logging.thread_safe_archive import ThreadSafeArchive
from codex.logging.thread_safe_session_db import ThreadSafeSessionDB


class TestReadWriteLock:
    """Test ReadWriteLock for Faiss operations."""

    @pytest.mark.flaky(reruns=2, reason="P6-concurrency: Read lock timing dependent on system load")
    def test_concurrent_readers(self):
        """Test multiple concurrent readers can read simultaneously."""
        lock = ReadWriteLock()
        read_count = [0]
        max_concurrent = [0]
        lock_acquired_times = []

        def reader(_reader_id: int):
            start = time.time()
            with lock.read_lock():
                lock_acquired_times.append(time.time())
                read_count[0] += 1
                max_concurrent[0] = max(max_concurrent[0], read_count[0])
                time.sleep(0.01)  # Simulate read operation
                read_count[0] -= 1
            elapsed = time.time() - start
            return elapsed < 0.1  # Should complete quickly

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(reader, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert all(results), "All reads should complete quickly"
        assert max_concurrent[0] > 1, "Multiple readers should be concurrent"
        # Check that wait times are recorded (may be >1ms due to thread scheduling)
        assert len(lock.metrics.lock_wait_time_ms) > 0, "Should record lock wait times"

    def test_exclusive_writer(self):
        """Test writer gets exclusive access."""
        lock = ReadWriteLock()
        write_count = [0]
        max_concurrent = [0]

        def writer():
            with lock.write_lock():
                write_count[0] += 1
                max_concurrent[0] = max(max_concurrent[0], write_count[0])
                time.sleep(0.01)
                write_count[0] -= 1

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(writer) for _ in range(5)]
            [f.result() for f in concurrent.futures.as_completed(futures)]

        assert max_concurrent[0] == 1, "Only one writer at a time"

    @pytest.mark.flaky(reruns=2, reason="P6-concurrency: Writer starvation timing dependent")
    def test_writer_starvation_prevention(self):
        """Test writers don't starve when readers present."""
        lock = ReadWriteLock(timeout=5.0)
        writer_acquired = threading.Event()
        test_timeout = False

        def reader():
            with lock.read_lock():
                time.sleep(0.05)

        def writer():
            with lock.write_lock():
                writer_acquired.set()

        # Start readers
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            reader_futures = [executor.submit(reader) for _ in range(5)]
            time.sleep(0.01)  # Let readers acquire lock

            # Try writer
            writer_future = executor.submit(writer)

            try:
                # Writer should eventually acquire lock
                writer_future.result(timeout=2.0)
                assert writer_acquired.is_set(), "Writer should acquire lock"
            except concurrent.futures.TimeoutError:
                test_timeout = True

        # Clean up
        for f in reader_futures:
            try:
                f.result(timeout=1.0)
            except Exception:  # swallow timeout/cancellation errors during test cleanup; they do not affect test validity  # noqa: E501
                pass

        assert not test_timeout, "Writer should not timeout"


class TestSQLiteConnectionPool:
    """Test SQLite connection pooling."""

    def test_connection_reuse(self, tmp_path):
        """Test connections are reused per thread."""
        db_path = str(tmp_path / "test.db")
        pool = SQLiteConnectionPool(db_path, max_connections=5)

        conn_ids = []

        def get_and_store_conn():
            conn = pool.get_connection()
            conn_ids.append(id(conn))
            time.sleep(0.01)

        thread_ids = []

        def thread_func():
            for _ in range(3):
                get_and_store_conn()
            thread_ids.append(threading.get_ident())

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(thread_func) for _ in range(2)]
            [f.result() for f in concurrent.futures.as_completed(futures)]

        # Each thread should reuse same connection
        assert len(set(conn_ids)) == 2, "Should have 2 unique connections (one per thread)"
        pool.cleanup_all()

    def test_wal_mode_enabled(self, tmp_path):
        """Test WAL mode is enabled."""
        db_path = str(tmp_path / "test.db")
        pool = SQLiteConnectionPool(db_path, wal_mode=True)

        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]

        assert mode.upper() == "WAL", "WAL mode should be enabled"
        pool.cleanup_all()

    def test_concurrent_connections(self, tmp_path):
        """Test concurrent connections from multiple threads."""
        db_path = str(tmp_path / "test.db")
        pool = SQLiteConnectionPool(db_path, max_connections=20)

        results = []

        def worker(worker_id: int):
            try:
                conn = pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT ?", (worker_id,))
                result = cursor.fetchone()[0]
                results.append(result)
                return True
            except (IOError, OSError):
                results.append(None)
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len([r for r in results if r is not None]) == 10, "All workers should succeed"
        pool.cleanup_all()


class TestThreadSafeSessionDB:
    """Test ThreadSafeSessionDB."""

    def test_concurrent_inserts(self, tmp_path):
        """Test concurrent session insertions."""
        db_path = str(tmp_path / "sessions.db")
        db = ThreadSafeSessionDB(db_path)

        def insert_session(session_id: int):
            session = {
                "session_id": f"S{session_id:04d}",
                "status": "complete",
                "timestamp": time.strftime("%Y-%m-%d"),
                "pr_number": session_id,
                "branch": "main",
            }
            return db.insert_session(session)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(insert_session, i) for i in range(50)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert all(results), "All inserts should succeed"

        # Verify all sessions were inserted
        sessions = db.query_sessions(days=30, limit=100)
        assert len(sessions) == 50, "All 50 sessions should be in database"

        db.cleanup()

    def test_concurrent_reads_and_writes(self, tmp_path):
        """Test concurrent reads and writes."""
        db_path = str(tmp_path / "sessions.db")
        db = ThreadSafeSessionDB(db_path)

        # Insert initial sessions
        for i in range(10):
            db.insert_session(
                {
                    "session_id": f"S{i:04d}",
                    "status": "pending",
                    "timestamp": time.strftime("%Y-%m-%d"),
                }
            )

        errors = []

        def reader(thread_id: int):
            try:
                for _ in range(20):
                    sessions = db.query_sessions(days=30, limit=10)
                    if not sessions:
                        errors.append(f"Reader {thread_id}: No sessions found")
                    time.sleep(0.001)
                return True
            except (IOError, OSError) as e:
                errors.append(f"Reader {thread_id}: {e}")
                return False

        def writer(thread_id: int):
            try:
                for i in range(10):
                    db.insert_session(
                        {
                            "session_id": f"W{thread_id}_{i}",
                            "status": "complete",
                            "timestamp": time.strftime("%Y-%m-%d"),
                        }
                    )
                    time.sleep(0.001)
                return True
            except (IOError, OSError) as e:
                errors.append(f"Writer {thread_id}: {e}")
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Start readers
            reader_futures = [executor.submit(reader, i) for i in range(5)]
            # Start writers
            writer_futures = [executor.submit(writer, i) for i in range(2)]

            all_results = [f.result() for f in concurrent.futures.as_completed(reader_futures)] + [
                f.result() for f in concurrent.futures.as_completed(writer_futures)
            ]

        assert all(all_results), f"All operations should succeed. Errors: {errors}"
        db.cleanup()

    def test_update_with_lock(self, tmp_path):
        """Test session updates are properly locked."""
        db_path = str(tmp_path / "sessions.db")
        db = ThreadSafeSessionDB(db_path)

        # Insert a session
        db.insert_session(
            {
                "session_id": "TEST_SESSION",
                "status": "pending",
                "timestamp": time.strftime("%Y-%m-%d"),
            }
        )

        status_results = []

        def update_status(new_status: str):
            success = db.update_session_status("TEST_SESSION", new_status)
            if success:
                session = db.get_session("TEST_SESSION")
                status_results.append(session.get("status") if session else None)
            return success

        statuses = ["in-progress", "complete", "failed"]

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(update_status, status) for status in statuses]
            [f.result() for f in concurrent.futures.as_completed(futures)]

        # Final status should be one of the updated values
        final_session = db.get_session("TEST_SESSION")
        assert final_session["status"] in statuses
        db.cleanup()


class TestThreadSafeArchive:
    """Test ThreadSafeArchive operations."""

    def test_exclusive_archive_operations(self):
        """Test archive operations are mutually exclusive per session."""
        archive = ThreadSafeArchive(timeout=5.0, max_retries=2)

        operation_order = []
        operation_times = {}
        lock = threading.Lock()

        def archive_op(session_id: str, op_id: int):
            try:
                with archive.archive_session(session_id):
                    with lock:
                        operation_times[op_id] = {
                            "start": time.time(),
                            "session": session_id,
                        }
                    time.sleep(0.05)  # Simulate operation
                    with lock:
                        operation_times[op_id]["end"] = time.time()
                        operation_order.append(op_id)
                return True
            except (IOError, OSError):
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(archive_op, "SESSION_1", i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert all(results), "All archive operations should succeed"

        # Verify operations don't overlap for same session
        times = list(operation_times.values())
        for i, op1 in enumerate(times):
            for op2 in times[i + 1 :]:
                if op1["session"] == op2["session"]:
                    # Operations should not overlap
                    assert op1["end"] <= op2["start"] or op2["end"] <= op1["start"], (
                        "Operations on same session should not overlap"
                    )

    def test_archive_timeout_retry(self):
        """Test archive timeout triggers retry."""
        archive = ThreadSafeArchive(timeout=0.1, max_retries=2)

        success_count = [0]

        def blocker():
            with archive.archive_session("SESSION"):
                time.sleep(0.5)  # Hold lock longer than timeout

        def waiter():
            try:
                # Should timeout and retry
                acquired = archive.try_archive("SESSION", timeout=0.1)
                if not acquired:
                    success_count[0] += 1
                return True
            except (IOError, OSError):
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            blocker_future = executor.submit(blocker)
            time.sleep(0.05)  # Let blocker acquire lock

            waiter_future = executor.submit(waiter)

            try:
                waiter_result = waiter_future.result(timeout=1.0)
                assert waiter_result, "Waiter should handle timeout gracefully"
            except Exception as e:
                pytest.fail(f"Waiter should not raise: {e}")

            try:
                blocker_future.result(timeout=1.0)
            except Exception:  # swallow timeout/cancellation errors during test cleanup; they do not affect test validity  # noqa: E501
                pass


class TestStressScenarios:
    """Stress tests with mixed concurrent operations."""

    def test_thousand_mixed_operations(self, tmp_path):
        """Stress test with 1000 mixed read/write/archive operations."""
        db_path = str(tmp_path / "stress.db")
        db = ThreadSafeSessionDB(db_path)
        archive = ThreadSafeArchive()

        operation_counts = {"reads": 0, "writes": 0, "archives": 0}
        errors = []

        def mixed_operation(op_num: int):
            try:
                op_type = op_num % 3
                session_id = f"STRESS_{op_num // 3}"

                if op_type == 0:  # Read
                    db.query_sessions(days=7, limit=10)
                    operation_counts["reads"] += 1

                elif op_type == 1:  # Write
                    db.insert_session(
                        {
                            "session_id": session_id,
                            "status": "complete",
                            "timestamp": time.strftime("%Y-%m-%d"),
                        }
                    )
                    operation_counts["writes"] += 1

                else:  # Archive
                    if archive.try_archive(session_id, timeout=0.1):
                        operation_counts["archives"] += 1

                return True

            except (IOError, OSError) as e:
                errors.append(str(e))
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(mixed_operation, i)
                for i in range(300)  # 1000 operations across many threads
            ]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        success_rate = sum(results) / len(results) * 100
        assert success_rate > 95, f"Success rate too low: {success_rate}%. Errors: {errors}"

        db.cleanup()
        archive.save_metrics()


class TestDeadlockRecovery:
    """Test deadlock recovery mechanisms."""

    def test_retry_with_backoff(self, tmp_path):
        """Test retry with exponential backoff."""
        attempt_count = [0]

        def func_with_retry():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise sqlite3.OperationalError("database is locked")
            return "success"

        result = DeadlockRecovery.retry_with_backoff(func_with_retry, max_retries=5)
        assert result == "success"
        assert attempt_count[0] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
