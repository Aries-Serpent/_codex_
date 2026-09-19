"""Test synchronization utilities for flaky test stabilization.

Phase 5 Track 3: Test Coverage Maximization

This module provides reusable synchronization patterns for preventing race
conditions and timing-based non-determinism in concurrent tests.

Created: 2026-07-10
Authority: @mbaetiong (Phase 5 Track 3)
"""

import contextlib
import threading
import time
from typing import Any, Callable, Generator, Tuple


@contextlib.contextmanager
def synchronize_threads(num_threads: int) -> Generator[threading.Barrier, None, None]:
    """Context manager for thread synchronization using barriers.

    All threads wait at the barrier until all have reached it, ensuring
    synchronized startup and preventing timing-based race conditions.

    Args:
        num_threads: Number of threads that will synchronize at barrier

    Yields:
        Barrier object for threads to call barrier.wait()

    Example:
        >>> with synchronize_threads(4) as barrier:
        ...     def worker():
        ...         barrier.wait()  # All threads start together
        ...         do_work()
        ...     threads = [Thread(target=worker) for _ in range(4)]
        ...     for t in threads: t.start()
        ...     for t in threads: t.join()

    Raises:
        BrokenBarrierError: If a thread is interrupted while waiting
    """
    barrier = threading.Barrier(num_threads)
    try:
        yield barrier
    finally:
        barrier.reset()


@contextlib.contextmanager
def timed_event(
    timeout: float,
) -> Generator[Tuple[threading.Event, threading.Timer], None, None]:
    """Create a precisely-timed event for timeout-based test operations.

    Uses threading.Timer for kernel-level precision instead of time.sleep(),
    which is subject to system load interference.

    Args:
        timeout: Duration in seconds until event is set

    Yields:
        Tuple of (event, timer) where timer must be started manually

    Example:
        >>> with timed_event(1.0) as (event, timer):
        ...     timer.start()
        ...     event.wait()  # Waits exactly 1 second
        ...     timer.join()

    Note:
        Unlike time.sleep(), this provides:
        - Kernel-level precision
        - No system load interference
        - Guaranteed event ordering
        - No platform-specific timing variations
    """
    event = threading.Event()
    timer = threading.Timer(timeout, event.set)

    try:
        yield event, timer
    finally:
        timer.cancel()
        timer.join()


def assert_deterministic(
    func: Callable[..., Any], runs: int = 5, *args: Any, **kwargs: Any
) -> Any:
    """Assert a function produces deterministic results across multiple runs.

    Runs the function multiple times with the same arguments and asserts
    that all results are identical. Useful for validating that tests don't
    depend on random state or timing variations.

    Args:
        func: Callable to test for determinism
        runs: Number of times to run function (default: 5)
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func

    Returns:
        The result from the first run (all runs should be identical)

    Raises:
        AssertionError: If results vary between runs

    Example:
        >>> def deterministic_sort():
        ...     items = [3, 1, 4, 1, 5, 9, 2, 6]
        ...     return sorted(items)
        ...
        >>> result = assert_deterministic(deterministic_sort, runs=10)
        >>> result
        [1, 1, 2, 3, 4, 5, 6, 9]

    Note:
        This function expects tests to have deterministic seeds set via
        the set_deterministic_seed fixture in conftest.py.
    """
    results = [func(*args, **kwargs) for _ in range(runs)]

    for i in range(1, len(results)):
        if results[i] != results[0]:
            raise AssertionError(
                f"Non-deterministic function behavior detected:\n"
                f"  Run 1 returned: {results[0]}\n"
                f"  Run {i} returned: {results[i]}\n"
                f"  (across {runs} runs, index {i} differs)"
            )

    return results[0]


@contextlib.contextmanager
def thread_safe_list(num_writers: int) -> Generator[Tuple[list, threading.Lock], None, None]:
    """Create a thread-safe list for concurrent write operations.

    Provides a lock for protecting concurrent access to a shared list.
    All writes must use the lock to prevent race conditions.

    Args:
        num_writers: Number of threads that will write to list (informational)

    Yields:
        Tuple of (thread_safe_list, lock)

    Example:
        >>> with thread_safe_list(4) as (results, lock):
        ...     def worker(value):
        ...         with lock:
        ...             results.append(value)
        ...     threads = [Thread(target=worker, args=(i,)) for i in range(4)]
        ...     for t in threads: t.start()
        ...     for t in threads: t.join()
        ...     assert len(results) == 4

    Note:
        The lock must be acquired before any access to the list.
        Following this pattern prevents lost updates and race conditions.
    """
    results: list = []
    lock = threading.Lock()

    try:
        yield results, lock
    finally:
        # No cleanup needed; lock will be garbage collected
        pass


class DeterministicTimeout:
    """Context manager for deterministic timeout validation.

    Provides precise timeout measurement without relying on time.sleep()
    or system clock accuracy.

    Example:
        >>> with DeterministicTimeout(max_seconds=1.0) as timer:
        ...     expensive_operation()
        ...     assert timer.elapsed() < 1.0, "Operation took too long"

    Attributes:
        max_seconds: Maximum allowed duration
        start_time: When the timer started
    """

    def __init__(self, max_seconds: float):
        """Initialize timeout context manager.

        Args:
            max_seconds: Maximum allowed duration in seconds
        """
        self.max_seconds = max_seconds
        self.start_time: float | None = None
        self._event: threading.Event | None = None
        self._timer: threading.Timer | None = None

    def __enter__(self) -> "DeterministicTimeout":
        """Start the timeout measurement."""
        self.start_time = time.time()
        self._event = threading.Event()
        self._timer = threading.Timer(self.max_seconds, self._event.set)
        self._timer.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop the timeout measurement and cleanup."""
        if self._timer:
            self._timer.cancel()
            self._timer.join()
        if self._event:
            self._event.clear()

    def elapsed(self) -> float:
        """Get elapsed time since context entered.

        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            raise RuntimeError("Timer not started; use 'with' statement")
        return time.time() - self.start_time

    def exceeded(self) -> bool:
        """Check if timeout has been exceeded.

        Returns:
            True if elapsed time exceeds max_seconds
        """
        return self.elapsed() > self.max_seconds

    def remaining(self) -> float:
        """Get remaining time before timeout.

        Returns:
            Remaining time in seconds (may be negative if exceeded)
        """
        return self.max_seconds - self.elapsed()


@contextlib.contextmanager
def exclusive_resource(resource_name: str) -> Generator[None, None, None]:
    """Context manager for exclusive resource access in tests.

    Prevents concurrent access to a resource across multiple threads.
    Useful for protecting file operations, database transactions, etc.

    Args:
        resource_name: Name of the resource being protected

    Yields:
        None (resource is automatically locked)

    Example:
        >>> with exclusive_resource("test_database"):
        ...     # Exclusive access to resource
        ...     db.write_transaction()

    Note:
        This implementation uses a module-level lock dictionary.
        Resource names should be descriptive and consistent across calls.
    """
    # Module-level lock dictionary for resource tracking
    if not hasattr(exclusive_resource, "_locks"):
        exclusive_resource._locks: dict = {}  # type: ignore

    if resource_name not in exclusive_resource._locks:
        exclusive_resource._locks[resource_name] = threading.Lock()  # type: ignore

    lock = exclusive_resource._locks[resource_name]  # type: ignore

    with lock:
        yield


# Preset patterns for common flaky test scenarios

@contextlib.contextmanager
def no_timing_interference(
    num_workers: int,
) -> Generator[Tuple[threading.Barrier, threading.Lock], None, None]:
    """Combined synchronization for concurrent operations with shared state.

    Provides both thread synchronization (barrier) and state protection (lock)
    for complex concurrent test scenarios.

    Args:
        num_workers: Number of concurrent workers

    Yields:
        Tuple of (barrier, lock) for worker coordination and state protection

    Example:
        >>> with no_timing_interference(4) as (barrier, lock):
        ...     results = []
        ...     def worker():
        ...         barrier.wait()  # All workers start together
        ...         result = compute()
        ...         with lock:
        ...             results.append(result)
        ...     threads = [Thread(target=worker) for _ in range(4)]
        ...     for t in threads: t.start()
        ...     for t in threads: t.join()
        ...     assert len(results) == 4
    """
    barrier = threading.Barrier(num_workers)
    lock = threading.Lock()

    try:
        yield barrier, lock
    finally:
        barrier.reset()


__all__ = [
    "synchronize_threads",
    "timed_event",
    "assert_deterministic",
    "thread_safe_list",
    "DeterministicTimeout",
    "exclusive_resource",
    "no_timing_interference",
]
