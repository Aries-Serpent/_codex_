"""
Phase 6: Concurrency Protection Module

Provides thread-safe access patterns for:
- SQLite database operations (RLock with connection pooling)
- Faiss index operations (ReadWriteLock: concurrent readers, exclusive writers)
- Archive operations (Mutex with timeout)
- Session query API (thread-safe queries and writes)

Includes monitoring for lock contention and deadlock recovery.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Generator, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class LockMetrics:
    """Tracks lock contention metrics."""

    lock_wait_time_ms: list[float] = field(default_factory=list)
    lock_contention_count: int = 0
    deadlock_retries: int = 0
    lock_held_count: int = 0
    max_wait_time_ms: float = 0.0

    def add_wait_time(self, wait_ms: float) -> None:
        """Record lock wait time and update max."""
        self.lock_wait_time_ms.append(wait_ms)
        self.max_wait_time_ms = max(self.max_wait_time_ms, wait_ms)
        if wait_ms > 1.0:  # Log contention if wait > 1ms
            self.lock_contention_count += 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "lock_wait_times_ms": self.lock_wait_time_ms[-100:],  # Keep last 100
            "lock_contention_count": self.lock_contention_count,
            "deadlock_retries": self.deadlock_retries,
            "lock_held_count": self.lock_held_count,
            "max_wait_time_ms": self.max_wait_time_ms,
            "avg_wait_time_ms": (
                sum(self.lock_wait_time_ms) / len(self.lock_wait_time_ms)
                if self.lock_wait_time_ms
                else 0.0
            ),
        }


class ReadWriteLock:
    """
    Read-Write Lock for Faiss index operations.

    Features:
    - Multiple concurrent readers
    - Single exclusive writer
    - No writer starvation
    - Timeout support (60 seconds)
    """

    def __init__(self, timeout: float = 60.0):
        """Initialize read-write lock."""
        self.timeout = timeout
        self._read_ready = threading.Condition(threading.RLock())
        self._readers = 0
        self._writers = 0
        self._write_waiters = 0
        self.metrics = LockMetrics()

    @contextmanager
    def read_lock(self) -> Generator[None, None, None]:
        """Acquire read lock (allow concurrent readers)."""
        start_time = time.time()
        acquired = False
        try:
            with self._read_ready:
                # Wait if writers are waiting (no writer starvation)
                deadline = time.time() + self.timeout
                while self._writers > 0 or self._write_waiters > 0:
                    remaining = deadline - time.time()
                    if remaining <= 0:
                        raise TimeoutError(
                            f"Read lock timeout after {self.timeout}s (writers waiting)"
                        )
                    if not self._read_ready.wait(timeout=remaining):
                        raise TimeoutError(f"Read lock timeout after {self.timeout}s")

                self._readers += 1
                acquired = True

            yield

        finally:
            wait_ms = (time.time() - start_time) * 1000
            self.metrics.add_wait_time(wait_ms)

            if acquired:
                with self._read_ready:
                    self._readers -= 1
                    if self._readers == 0:
                        self._read_ready.notify_all()

    @contextmanager
    def write_lock(self) -> Generator[None, None, None]:
        """Acquire write lock (exclusive, single writer)."""
        start_time = time.time()
        acquired = False
        try:
            with self._read_ready:
                self._write_waiters += 1
                try:
                    # Wait for all readers to finish
                    deadline = time.time() + self.timeout
                    while self._readers > 0 or self._writers > 0:
                        remaining = deadline - time.time()
                        if remaining <= 0:
                            raise TimeoutError(
                                f"Write lock timeout after {self.timeout}s (readers: "
                                f"{self._readers}, writers: {self._writers})"
                            )
                        if not self._read_ready.wait(timeout=remaining):
                            raise TimeoutError(f"Write lock timeout after {self.timeout}s")

                    self._writers += 1
                    acquired = True
                finally:
                    self._write_waiters -= 1

            yield

        finally:
            wait_ms = (time.time() - start_time) * 1000
            self.metrics.add_wait_time(wait_ms)

            if acquired:
                with self._read_ready:
                    self._writers -= 1
                    self._read_ready.notify_all()


class SQLiteConnectionPool:
    """
    Thread-safe SQLite connection pool with per-thread connections.

    Features:
    - Per-thread connection reuse (up to 20 connections)
    - Automatic connection cleanup
    - WAL mode enabled for concurrent access
    - Timeout handling (30 seconds)
    - Connection validation
    """

    def __init__(
        self,
        db_path: str,
        max_connections: int = 20,
        timeout: float = 30.0,
        wal_mode: bool = True,
    ):
        """Initialize connection pool."""
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self._lock = threading.RLock()
        self._connections: dict[int, sqlite3.Connection] = {}
        self._thread_ids: set[int] = set()
        self.wal_mode = wal_mode
        self.metrics = LockMetrics()

        # Enable WAL mode on database
        if wal_mode:
            self._enable_wal_mode()

    def _enable_wal_mode(self) -> None:
        """Enable WAL (Write-Ahead Logging) mode for concurrent writes."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.timeout)
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
            conn.close()
            logger.info(f"WAL mode enabled for {self.db_path}")
        except sqlite3.Error as e:
            type(e).__name__
            logger.warning("Failed to enable WAL mode: <ERROR_TYPE>")

    def get_connection(self) -> sqlite3.Connection:
        """Get thread-local connection (creates if needed)."""
        thread_id = threading.get_ident()
        start_time = time.time()

        with self._lock:
            if thread_id not in self._connections:
                if len(self._connections) >= self.max_connections:
                    raise RuntimeError(f"Connection pool exhausted ({self.max_connections} max)")
                conn = sqlite3.connect(self.db_path, timeout=self.timeout)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON")
                self._connections[thread_id] = conn
                self._thread_ids.add(thread_id)
                logger.debug(f"Created connection for thread {thread_id}")

            conn = self._connections[thread_id]

        wait_ms = (time.time() - start_time) * 1000
        self.metrics.add_wait_time(wait_ms)
        return conn

    def close_connection(self, thread_id: Optional[int] = None) -> None:
        """Close thread-local connection."""
        if thread_id is None:
            thread_id = threading.get_ident()

        with self._lock:
            if thread_id in self._connections:
                conn = self._connections[thread_id]
                try:
                    conn.close()
                    logger.debug(f"Closed connection for thread {thread_id}")
                except sqlite3.Error as e:
                    type(e).__name__
                    logger.warning("Error closing connection: <ERROR_TYPE>")
                finally:
                    del self._connections[thread_id]
                    self._thread_ids.discard(thread_id)

    def cleanup_all(self) -> None:
        """Close all connections in the pool."""
        with self._lock:
            for conn in self._connections.values():
                try:
                    conn.close()
                except sqlite3.Error:
                    pass
            self._connections.clear()
            self._thread_ids.clear()


class ArchiveOperationLock:
    """
    Mutex for archive operations.

    Features:
    - Single operation at a time (mutually exclusive)
    - Prevents simultaneous archive + retrieval on same session
    - 60-second timeout
    - Auto-retry with exponential backoff
    """

    def __init__(self, timeout: float = 60.0, max_retries: int = 3):
        """Initialize archive lock."""
        self.timeout = timeout
        self.max_retries = max_retries
        self._lock = threading.Lock()
        self._session_locks: dict[str, threading.Lock] = {}
        self._session_lock = threading.RLock()
        self.metrics = LockMetrics()

    def acquire_session_lock(self, session_id: str) -> threading.Lock:
        """Get or create lock for specific session."""
        with self._session_lock:
            if session_id not in self._session_locks:
                self._session_locks[session_id] = threading.Lock()
            return self._session_locks[session_id]

    @contextmanager
    def archive_lock(self, session_id: str) -> Generator[None, None, None]:
        """Acquire exclusive lock for archive operation."""
        lock = self.acquire_session_lock(session_id)
        start_time = time.time()
        retries = 0

        while retries < self.max_retries:
            try:
                acquired = lock.acquire(timeout=self.timeout)
                if not acquired:
                    retries += 1
                    self.metrics.deadlock_retries += 1
                    wait_ms = (time.time() - start_time) * 1000
                    logger.warning(
                        f"Archive lock timeout for {session_id}, "
                        f"retry {retries}/{self.max_retries} (waited {wait_ms}ms)"
                    )
                    if retries >= self.max_retries:
                        raise TimeoutError(
                            f"Archive lock timeout after {self.max_retries} retries "
                            f"({self.timeout}s each)"
                        )
                    time.sleep(min(2**retries, 10))  # Exponential backoff
                    continue

                self.metrics.lock_held_count += 1
                try:
                    yield
                finally:
                    lock.release()
                    wait_ms = (time.time() - start_time) * 1000
                    self.metrics.add_wait_time(wait_ms)
                break

            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.error(f"Archive lock error for {session_id}: <ERROR_TYPE>")
                raise


class DeadlockRecovery:
    """Handles deadlock recovery with exponential backoff."""

    @staticmethod
    def retry_with_backoff(
        func: Callable[..., T],
        max_retries: int = 3,
        base_delay: float = 0.1,
    ) -> T:
        """Retry function with exponential backoff on deadlock."""
        last_error = None

        for attempt in range(max_retries):
            try:
                return func()
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) or "locked" in str(e).lower():
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = base_delay * (2**attempt)
                        logger.warning(
                            f"Database locked, retry {attempt + 1}/{max_retries} after {wait_time}s"
                        )
                        time.sleep(wait_time)
                    else:
                        raise
                else:
                    raise

        raise last_error or RuntimeError("Max retries exceeded")


def save_metrics(
    metrics_dict: dict[str, dict[str, Any]],
    output_path: str = ".codex/concurrency_metrics.json",
) -> None:
    """Save metrics to JSON file."""
    import json

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_file, "w") as f:
            json.dump(metrics_dict, f, indent=2, default=str)
        logger.info(f"Metrics saved to {output_path}")
    except (IOError, OSError) as e:
        type(e).__name__
        logger.error("Failed to save metrics: <ERROR_TYPE>")


def log_error(
    error: Exception,
    context: str,
    log_path: str = ".codex/concurrency_errors.log",
) -> None:
    """Log error to concurrency errors file."""
    error_file = Path(log_path)
    error_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(error_file, "a") as f:
            f.write(f"[{timestamp}] {context}: {error}\n")
    except (IOError, OSError) as e:
        type(e).__name__
        logger.error("Failed to log error: <ERROR_TYPE>")
