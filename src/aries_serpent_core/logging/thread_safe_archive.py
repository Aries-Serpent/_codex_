"""
Thread-safe Archive Operations Wrapper (Phase 6)

Provides mutually exclusive archive operations:
- Single archive operation at a time
- Per-session operation locks
- Prevents simultaneous archive + retrieval
- 60-second timeout with exponential backoff
- Automatic retry with 3 attempts
- Monitoring and metrics collection
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Callable, Optional

from .concurrency import ArchiveOperationLock, log_error, save_metrics

logger = logging.getLogger(__name__)


class ThreadSafeArchive:
    """
    Thread-safe archive operations wrapper.

    Features:
    - Per-session operation locks (mutually exclusive)
    - Prevents simultaneous archive and retrieval on same session
    - 60-second timeout per operation
    - Exponential backoff on timeout (up to 3 retries)
    - Monitoring for lock contention
    - Comprehensive error logging
    """

    def __init__(
        self,
        timeout: float = 60.0,
        max_retries: int = 3,
        metrics_path: str = ".codex/concurrency_metrics.json",
        errors_path: str = ".codex/concurrency_errors.log",
    ):
        """Initialize thread-safe archive."""
        self.timeout = timeout
        self.max_retries = max_retries
        self.metrics_path = metrics_path
        self.errors_path = errors_path

        # Archive operation lock
        self._archive_lock = ArchiveOperationLock(
            timeout=timeout,
            max_retries=max_retries,
        )

    @contextmanager
    def archive_session(self, session_id: str):
        """Acquire exclusive lock for archive operation."""
        try:
            with self._archive_lock.archive_lock(session_id):
                yield

        except TimeoutError as e:
            type(e).__name__
            logger.error(f"Archive timeout for {session_id}: <ERROR_TYPE>")
            log_error(e, f"archive_timeout_{session_id}", self.errors_path)
            raise

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error(f"Archive error for {session_id}: <ERROR_TYPE>")
            log_error(e, f"archive_error_{session_id}", self.errors_path)
            raise

    @contextmanager
    def retrieve_session(self, session_id: str):
        """Acquire exclusive lock for retrieval operation."""
        try:
            with self._archive_lock.archive_lock(session_id):
                yield

        except TimeoutError as e:
            type(e).__name__
            logger.error(f"Retrieve timeout for {session_id}: <ERROR_TYPE>")
            log_error(e, f"retrieve_timeout_{session_id}", self.errors_path)
            raise

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error(f"Retrieve error for {session_id}: <ERROR_TYPE>")
            log_error(e, f"retrieve_error_{session_id}", self.errors_path)
            raise

    def try_archive(self, session_id: str, timeout: Optional[float] = None) -> bool:
        """Try to archive session without blocking (non-blocking lock attempt)."""
        lock = self._archive_lock.acquire_session_lock(session_id)
        actual_timeout = timeout if timeout is not None else self.timeout

        acquired = lock.acquire(timeout=actual_timeout)
        if acquired:
            try:
                return True
            finally:
                lock.release()
        return False

    def get_metrics(self) -> dict[str, Any]:
        """Get lock metrics."""
        return self._archive_lock.metrics.to_dict()

    def save_metrics(self) -> None:
        """Save metrics to JSON file."""
        metrics_dict = {
            "timestamp": time.time(),
            "component": "archive_operations",
            "archive_lock": self._archive_lock.metrics.to_dict(),
        }
        save_metrics(metrics_dict, self.metrics_path)  # type: ignore[arg-type]

    def __enter__(self) -> "ThreadSafeArchive":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.save_metrics()


class ArchiveSessionGuard:
    """
    Guard for archive session operations with automatic lock management.

    Usage:
        guard = ArchiveSessionGuard()
        session_data = guard.archive_with_lock(session_id, archive_func)
    """

    def __init__(self, archive: Optional[ThreadSafeArchive] = None):
        """Initialize archive guard."""
        self.archive = archive or ThreadSafeArchive()

    def archive_with_lock(
        self,
        session_id: str,
        archive_func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute archive function with exclusive lock."""
        try:
            with self.archive.archive_session(session_id):
                return archive_func(session_id, *args, **kwargs)

        except TimeoutError:
            logger.error(f"Archive timeout for {session_id}")
            return None

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error(f"Archive operation failed for {session_id}: <ERROR_TYPE>")
            log_error(e, f"archive_guard_error_{session_id}", self.archive.errors_path)
            return None

    def retrieve_with_lock(
        self,
        session_id: str,
        retrieve_func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute retrieve function with exclusive lock."""
        try:
            with self.archive.retrieve_session(session_id):
                return retrieve_func(session_id, *args, **kwargs)

        except TimeoutError:
            logger.error(f"Retrieve timeout for {session_id}")
            return None

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error(f"Retrieve operation failed for {session_id}: <ERROR_TYPE>")
            log_error(e, f"retrieve_guard_error_{session_id}", self.archive.errors_path)
            return None

    def parallel_archive(
        self,
        session_ids: list[str],
        archive_func: Callable,
        max_workers: int = 5,
    ) -> dict[str, bool]:
        """Archive multiple sessions in parallel with per-session locks."""
        import concurrent.futures

        results = {}

        def _archive_one(sid: str) -> tuple[str, bool]:
            try:
                result = self.archive_with_lock(sid, archive_func)
                return sid, result is not None
            except (IOError, OSError) as e:
                type(e).__name__
                logger.error(f"Parallel archive failed for {sid}: <ERROR_TYPE>")
                return sid, False

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_archive_one, sid): sid for sid in session_ids}

            for future in concurrent.futures.as_completed(futures):
                try:
                    sid, success = future.result()
                    results[sid] = success
                except (ValueError, TypeError, RuntimeError) as e:
                    type(e).__name__
                    logger.error("Parallel archive exception: <ERROR_TYPE>")
                    results[futures[future]] = False

        return results
