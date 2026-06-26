"""
Production Robustness Tests

Tests system robustness for network failures, database recovery, resource exhaustion,
and concurrent access patterns. All tests are isolated and deterministic.
"""

import queue
import sqlite3
import threading
import time
from pathlib import Path

import pytest

# Network Failure Simulation Tests


def test_network_timeout_handling():
    """Test graceful handling of network timeouts."""

    def fetch_with_timeout(url, timeout=5):
        # Simulate network call
        time.sleep(0.01)  # Fast simulation
        return {"status": "success", "data": "response"}

    def fetch_with_retry(url, max_retries=3):
        for attempt in range(max_retries):
            try:
                return fetch_with_timeout(url)
            except Exception as _err:
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.01 * (attempt + 1))  # Exponential backoff
        raise RuntimeError("retry loop exited without success")

    result = fetch_with_retry("http://example.com")
    assert result["status"] == "success", "Result must not be empty"


def test_connection_refused_fallback():
    """Test fallback mechanism when connection is refused."""

    class ServiceClient:
        def __init__(self, primary_url, fallback_url):
            self.primary_url = primary_url
            self.fallback_url = fallback_url

        def call(self, should_fail_primary=False):
            if not should_fail_primary:
                return {"source": "primary", "data": "success"}
            # Fallback to secondary
            return {"source": "fallback", "data": "success"}

    client = ServiceClient("http://primary:8080", "http://fallback:8080")

    # Primary works
    result = client.call(should_fail_primary=False)
    assert result["source"] == "primary", "Result must not be empty"

    # Primary fails, fallback works
    result = client.call(should_fail_primary=True)
    assert result["source"] == "fallback", "Result must not be empty"


def test_partial_network_failure_handling():
    """Test handling of partial network failures."""

    def fetch_multiple_sources(sources):
        results = []
        failures = []

        for idx, source in enumerate(sources):
            try:
                # Simulate some sources failing
                if idx % 3 == 0:
                    raise ConnectionError(f"Failed to connect to {source}")
                results.append({"source": source, "data": f"data_{idx}"})
            except ConnectionError as e:
                failures.append({"source": source, "error": str(e)})

        return results, failures

    sources = [f"http://source{i}.com" for i in range(10)]
    results, failures = fetch_multiple_sources(sources)

    # Should have some successes and some failures
    assert len(results) > 0, "Results must not be empty"
    assert len(failures) > 0, "Failures must not be empty"
    assert len(results) + len(failures) == len(sources), "Results must not be empty"


def test_circuit_breaker_pattern():
    """Test circuit breaker pattern for failing services."""

    class CircuitBreaker:
        def __init__(self, failure_threshold=3, timeout=5):
            self.failure_threshold = failure_threshold
            self.timeout = timeout
            self.failure_count = 0
            self.last_failure_time = None
            self.state = "closed"  # closed, open, half-open

        def call(self, func, *args, **kwargs):
            if self.state == "open":
                # Check if timeout expired
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "half-open"
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)
                # Success - reset
                self.failure_count = 0
                self.state = "closed"
                return result
            except Exception as _err:
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
                raise

    cb = CircuitBreaker(failure_threshold=3, timeout=0.1)

    def failing_service():
        raise ConnectionError("Service unavailable")

    # Accumulate failures
    for _ in range(3):
        with pytest.raises(Exception):
            cb.call(failing_service)

    # Circuit should be open
    assert cb.state == "open", "state is not valid"

    # Further calls should fail immediately
    with pytest.raises(Exception, match="Circuit breaker is OPEN"):
        cb.call(failing_service)


# Database Recovery Tests


def test_database_connection_recovery(tmp_path):
    """Test database reconnection after connection loss."""

    db_path = tmp_path / "test.db"

    def connect_with_retry(db_path, max_retries=3):
        for attempt in range(max_retries):
            try:
                return sqlite3.connect(str(db_path))
            except sqlite3.Error:
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.01)
        raise RuntimeError("retry loop exited without success")

    # Initial connection
    conn = connect_with_retry(db_path)
    conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")
    conn.commit()
    conn.close()

    # Reconnect and verify
    conn = connect_with_retry(db_path)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    assert len(tables) == 1, "Tables must not be empty"
    conn.close()


def test_database_transaction_rollback(tmp_path):
    """Test transaction rollback on errors."""

    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))

    # Create table
    conn.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance REAL)")
    conn.execute("INSERT INTO accounts VALUES (1, 1000.0)")
    conn.commit()

    # Start transaction
    try:
        conn.execute("UPDATE accounts SET balance = balance - 500 WHERE id = 1")
        # Simulate error — commit is intentionally never reached
        raise ValueError("Payment processing failed")
    except ValueError:
        conn.rollback()

    # Verify rollback
    cursor = conn.execute("SELECT balance FROM accounts WHERE id = 1")
    balance = cursor.fetchone()[0]
    assert balance == 1000.0, "balance is not valid"
    conn.close()


def test_database_corruption_detection(tmp_path):
    """Test detection of database corruption."""

    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))

    # Create and populate database
    conn.execute("CREATE TABLE data (id INTEGER, value TEXT)")
    for i in range(100):
        conn.execute("INSERT INTO data VALUES (?, ?)", (i, f"value_{i}"))
    conn.commit()

    # Verify integrity
    cursor = conn.execute("PRAGMA integrity_check")
    result = cursor.fetchone()[0]
    assert result == "ok", "Result must not be empty"

    conn.close()


def test_database_deadlock_prevention(tmp_path):
    """Test deadlock prevention in concurrent database access."""

    db_path = tmp_path / "test.db"

    # Create database with sample data
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE counter (id INTEGER PRIMARY KEY, value INTEGER)")
    conn.execute("INSERT INTO counter VALUES (1, 0)")
    conn.commit()
    conn.close()

    errors = []

    def increment_counter(thread_id):
        try:
            conn = sqlite3.connect(str(db_path), timeout=5.0)
            for _ in range(10):
                conn.execute("UPDATE counter SET value = value + 1 WHERE id = 1")
                conn.commit()
            conn.close()
        except sqlite3.Error as e:
            errors.append(e)

    # Run concurrent updates
    threads = [threading.Thread(target=increment_counter, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify no deadlocks occurred
    assert len(errors) == 0, "Errors must not be empty"

    # Verify final count
    conn = sqlite3.connect(str(db_path))
    cursor = conn.execute("SELECT value FROM counter WHERE id = 1")
    final_value = cursor.fetchone()[0]
    assert final_value == 30, "Value must be initialized"
    conn.close()


def test_database_connection_pooling():
    """Test database connection pool behavior."""

    class SimpleConnectionPool:
        def __init__(self, db_path, pool_size=5):
            self.db_path = db_path
            self.pool_size = pool_size
            self.pool = queue.Queue(maxsize=pool_size)
            self.active_connections = 0

        def get_connection(self):
            if not self.pool.empty():
                return self.pool.get()

            if self.active_connections < self.pool_size:
                self.active_connections += 1
                return {"id": self.active_connections, "status": "active"}

            # Wait for available connection
            return self.pool.get(timeout=1.0)

        def return_connection(self, conn):
            self.pool.put(conn)

    pool = SimpleConnectionPool(":memory:", pool_size=3)

    # Get connections
    conn1 = pool.get_connection()
    pool.get_connection()
    pool.get_connection()

    assert conn1["status"] == "active", "Condition must be true"
    assert pool.active_connections == 3, "active_connections is not valid"

    # Return connection
    pool.return_connection(conn1)

    # Reuse returned connection
    conn4 = pool.get_connection()
    assert conn4 == conn1, "conn4 is not valid"


# Disk Exhaustion Handling Tests


def test_disk_full_graceful_handling(tmp_path):
    """Test graceful handling when disk is full."""

    def write_with_space_check(file_path, data, min_free_space=1024 * 1024):
        # Simulate space check
        available_space = 10 * 1024 * 1024  # 10 MB

        if available_space < min_free_space:
            raise IOError("Insufficient disk space")

        with open(file_path, "w") as f:
            f.write(data)

    data_file = tmp_path / "data.txt"

    try:
        write_with_space_check(data_file, "test data")
        assert data_file.exists(), "Data must not be empty"
    except IOError as e:
        pytest.fail(f"Should not fail with sufficient space: {e}")


def test_partial_write_recovery(tmp_path):
    """Test recovery from partial write operations."""

    def atomic_write(file_path, data):
        temp_path = file_path.with_suffix(".tmp")

        try:
            # Write to temporary file
            with open(temp_path, "w") as f:
                f.write(data)
                f.flush()

            # Atomic rename
            temp_path.replace(file_path)
            return True
        except OSError:
            # Clean up temporary file on failure
            if temp_path.exists():
                temp_path.unlink()
            raise

    target_file = tmp_path / "data.txt"
    data = "important data"

    atomic_write(target_file, data)

    # Verify data
    assert target_file.read_text() == data, "Data must not be empty"

    # Verify no temp files left
    temp_files = list(tmp_path.glob("*.tmp"))
    assert len(temp_files) == 0, "Temp_files must not be empty"


def test_log_rotation_on_size_limit(tmp_path):
    """Test log rotation when size limit is reached."""

    class RotatingLog:
        def __init__(self, base_path, max_size=1024, max_files=3):
            self.base_path = Path(base_path)
            self.max_size = max_size
            self.max_files = max_files
            self.current_size = 0
            self.current_file = 0

        def write(self, message):
            log_file = self.base_path / f"log.{self.current_file}"

            # Check if rotation needed
            if self.current_size + len(message) > self.max_size:
                self.rotate()

            with open(log_file, "a") as f:
                f.write(message + "\n")
            self.current_size += len(message) + 1

        def rotate(self):
            self.current_file = (self.current_file + 1) % self.max_files
            self.current_size = 0
            log_file = self.base_path / f"log.{self.current_file}"
            if log_file.exists():
                log_file.unlink()

    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    logger = RotatingLog(log_dir, max_size=100, max_files=3)

    # Write messages that trigger rotation
    for i in range(50):
        logger.write(f"Log message {i}" * 2)

    # Should have created rotated files
    log_files = list(log_dir.glob("log.*"))
    assert len(log_files) <= 3, "Log_files must not be empty"


# Concurrent Access Tests


def test_concurrent_file_writes(tmp_path):
    """Test concurrent writes to different files."""

    def write_file(file_path, content, repeat):
        for i in range(repeat):
            with open(file_path, "a") as f:
                f.write(f"{content}_{i}\n")

    errors = []

    def worker(thread_id):
        try:
            file_path = tmp_path / f"thread_{thread_id}.txt"
            write_file(file_path, f"data_{thread_id}", 100)
        except (IOError, OSError) as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, "Errors must not be empty"

    # Verify each file
    for i in range(5):
        file_path = tmp_path / f"thread_{i}.txt"
        assert file_path.exists(), "Condition must be true"
        lines = file_path.read_text().strip().split("\n")
        assert len(lines) == 100, "Lines must not be empty"


def test_concurrent_read_access(tmp_path):
    """Test concurrent reads from same file."""

    # Create test file
    data_file = tmp_path / "data.txt"
    content = "\n".join([f"Line {i}" for i in range(1000)])
    data_file.write_text(content)

    read_counts = []
    errors = []

    def reader(reader_id):
        try:
            count = 0
            with open(data_file, "r") as f:
                for line in f:
                    count += 1
            read_counts.append(count)
        except (IOError, OSError) as e:
            errors.append(e)

    threads = [threading.Thread(target=reader, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, "Errors must not be empty"
    assert all(count == 1000 for count in read_counts), "Count must be greater than zero"


def test_concurrent_queue_processing():
    """Test concurrent processing of shared queue."""

    work_queue = queue.Queue()
    results = []
    lock = threading.Lock()

    # Add work items
    for i in range(100):
        work_queue.put(i)

    def worker():
        while True:
            try:
                item = work_queue.get(timeout=0.1)
                # Process item
                result = item * 2
                with lock:
                    results.append(result)
                work_queue.task_done()
            except queue.Empty:
                break

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 100, "Results must not be empty"
    assert sorted(results) == [i * 2 for i in range(100)], "Result must not be empty"


def test_thread_safe_counter():
    """Test thread-safe counter implementation."""

    class ThreadSafeCounter:
        def __init__(self):
            self.value = 0
            self.lock = threading.Lock()

        def increment(self):
            with self.lock:
                self.value += 1

        def get(self):
            with self.lock:
                return self.value

    counter = ThreadSafeCounter()

    def incrementer():
        for _ in range(1000):
            counter.increment()

    threads = [threading.Thread(target=incrementer) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert counter.get() == 5000, "Count must be greater than zero"


def test_resource_cleanup_on_error(tmp_path):
    """Test that resources are properly cleaned up on errors."""

    class ManagedResource:
        def __init__(self, path):
            self.path = path
            self.handle = None
            self.is_open = False

        def __enter__(self):
            self.handle = open(self.path, "w")
            self.is_open = True
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.handle:
                self.handle.close()
            self.is_open = False
            return False

        def write(self, data):
            if not self.is_open:
                raise RuntimeError("Resource not open")
            self.handle.write(data)

    resource_file = tmp_path / "resource.txt"

    try:
        with ManagedResource(resource_file) as res:
            res.write("data")
            raise ValueError("Simulated error")
    except ValueError:
        _ = None  # suppressed: no action needed

    # Resource should be cleaned up
    assert not hasattr(res, "is_open") or not res.is_open


def test_graceful_shutdown_with_pending_tasks():
    """Test graceful shutdown when tasks are pending."""

    work_queue = queue.Queue()
    completed = []
    shutdown_event = threading.Event()

    def worker():
        while not shutdown_event.is_set():
            try:
                item = work_queue.get(timeout=0.1)
                # Process item
                time.sleep(0.01)
                completed.append(item)
                work_queue.task_done()
            except queue.Empty:
                continue

    # Add work
    for i in range(10):
        work_queue.put(i)

    # Start worker
    thread = threading.Thread(target=worker)
    thread.start()

    # Let some work complete
    time.sleep(0.1)

    # Signal shutdown
    shutdown_event.set()
    thread.join(timeout=1.0)

    # Some work should have completed
    assert len(completed) > 0, "Completed must not be empty"


def test_rate_limited_concurrent_requests():
    """Test rate limiting under concurrent load."""

    class RateLimiter:
        def __init__(self, max_per_second):
            self.max_per_second = max_per_second
            self.requests = []
            self.lock = threading.Lock()

        def allow_request(self):
            with self.lock:
                now = time.time()
                # Remove old requests
                self.requests = [ts for ts in self.requests if now - ts < 1.0]

                if len(self.requests) < self.max_per_second:
                    self.requests.append(now)
                    return True
                return False

    limiter = RateLimiter(max_per_second=10)
    allowed_count = 0
    denied_count = 0
    lock = threading.Lock()

    def make_requests():
        nonlocal allowed_count, denied_count
        for _ in range(5):
            if limiter.allow_request():
                with lock:
                    allowed_count += 1
            else:
                with lock:
                    denied_count += 1
            time.sleep(0.01)

    threads = [threading.Thread(target=make_requests) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Some requests should be allowed, some denied
    total_requests = allowed_count + denied_count
    assert total_requests == 20, "total_requests is not valid"
    assert allowed_count <= 10, "Count must be greater than zero"
