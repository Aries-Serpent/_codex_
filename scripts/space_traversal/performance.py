#!/usr/bin/env python3
"""
Performance

Purpose:
    [To be documented - Performance]

Usage:
    python scripts/space_traversal/performance.py [options]

    Examples:
    $ python scripts/space_traversal/performance.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

from __future__ import annotations

# Performance optimizations for v1.5.5
#
# Provides performance utilities for audit pipeline operations.
#
# Features:
# - Function timing decorator
# - Disk-based caching with TTL
# - Batch file reading
# - Memory-efficient operations
#
# Example:
#     from scripts.space_traversal.performance import timed, FileCache
#
#     @timed
#     def expensive_operation():
#         pass
#
#     cache = FileCache(Path(".cache"))
#     if (result := cache.get("key")) is None:
#         result = compute()
#         cache.set("key", result, ttl_seconds=3600)
import functools
import hashlib
import json
import logging
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional, TypeVar

logger = logging.getLogger(__name__)

__all__ = [
    "timed",
    "FileCache",
    "batch_file_read",
    "PerformanceMetrics",
    "profile_stage",
]

F = TypeVar("F", bound=Callable[..., Any])


def timed(func: F) -> F:
    """
    Decorator to time function execution.

    Prints execution time to stdout after function completes.

    Args:
        func: Function to time

    Returns:
        Wrapped function
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  {func.__name__}: {elapsed:.3f}s")
        return result

    return wrapper  # type: ignore


class FileCache:
    """Disk-based cache for expensive computations."""

    def __init__(self, cache_dir: Path):
        """
        Initialize file cache.

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, key: str) -> Path:
        """Generate cache file path from key."""
        hashed = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self.cache_dir / f"{hashed}.json"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        path = self._cache_key(key)
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                    expires_at = data.get("expires_at")
                    if expires_at is None or expires_at > time.time():
                        return data.get("value")
                    # Expired - remove file
                    path.unlink(missing_ok=True)
            except (OSError, json.JSONDecodeError) as e:
                logger.debug(f"Exception: {e}")
                # Corrupt or unreadable cache file; log and treat as cache miss.
                logger.debug(f"Cache read error for key '{key}': {e}")
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl_seconds: Time-to-live in seconds
        """
        path = self._cache_key(key)
        expires_at = time.time() + ttl_seconds if ttl_seconds > 0 else None
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "value": value,
                    "expires_at": expires_at,
                    "created_at": time.time(),
                },
                f,
            )

    def invalidate(self, key: str) -> bool:
        """
        Invalidate a cache entry.

        Args:
            key: Cache key

        Returns:
            True if entry was removed, False if not found
        """
        path = self._cache_key(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        count = 0
        for path in self.cache_dir.glob("*.json"):
            path.unlink()
            count += 1
        return count

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        count = 0
        now = time.time()
        for path in self.cache_dir.glob("*.json"):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                    expires_at = data.get("expires_at")
                    if expires_at is not None and expires_at <= now:
                        path.unlink()
                        count += 1
            except (OSError, json.JSONDecodeError) as e:
                logger.debug(f"Exception: {e}")
                # Corrupt or unreadable cache file during cleanup; log for manual intervention.
                logger.warning(f"Unable to clean cache file '{path}': {e}")
        return count


def batch_file_read(
    file_paths: list[Path],
    max_size: int = 200_000,
    encoding: str = "utf-8",
) -> dict[str, str]:
    """
    Efficiently read multiple files in batch.

    Args:
        file_paths: List of file paths to read
        max_size: Maximum file size to read (bytes)
        encoding: Text encoding

    Returns:
        Dictionary mapping path strings to file contents
    """
    results: dict[str, str] = {}
    for path in file_paths:
        try:
            if path.exists() and path.stat().st_size <= max_size:
                results[str(path)] = path.read_text(encoding=encoding, errors="ignore")
        except OSError:
            # Intentionally ignore file read errors; skip unreadable files.
            logger.debug("Suppressed exception in handler", exc_info=True)
    return results


class PerformanceMetrics:
    """Collect and report performance metrics."""

    def __init__(self):
        self.metrics: list[dict[str, Any]] = []
        self._stage_start: Optional[float] = None
        self._current_stage: Optional[str] = None

    def start_stage(self, stage: str) -> None:
        """Start timing a stage."""
        self._current_stage = stage
        self._stage_start = time.perf_counter()

    def end_stage(self, **extra: Any) -> float:
        """
        End timing current stage.

        Args:
            **extra: Additional metadata to record

        Returns:
            Elapsed time in seconds
        """
        if self._stage_start is None or self._current_stage is None:
            return 0.0

        elapsed = time.perf_counter() - self._stage_start
        self.metrics.append(
            {
                "stage": self._current_stage,
                "duration_seconds": round(elapsed, 6),
                "timestamp": time.time(),
                **extra,
            }
        )
        self._stage_start = None
        self._current_stage = None
        return elapsed

    def record(self, stage: str, duration: float, **extra: Any) -> None:
        """
        Record a metric directly.

        Args:
            stage: Stage name
            duration: Duration in seconds
            **extra: Additional metadata
        """
        self.metrics.append(
            {
                "stage": stage,
                "duration_seconds": round(duration, 6),
                "timestamp": time.time(),
                **extra,
            }
        )

    def summary(self) -> dict[str, Any]:
        """
        Get performance summary.

        Returns:
            Dictionary with total time, stage times, and statistics
        """
        if not self.metrics:
            return {"total_seconds": 0, "stages": {}, "count": 0}

        total = sum(m["duration_seconds"] for m in self.metrics)
        stages: dict[str, float] = {}
        for m in self.metrics:
            stage = m["stage"]
            stages[stage] = stages.get(stage, 0) + m["duration_seconds"]

        return {
            "total_seconds": round(total, 3),
            "stages": {k: round(v, 3) for k, v in sorted(stages.items())},
            "count": len(self.metrics),
            "slowest_stage": max(stages.items(), key=lambda x: x[1])[0] if stages else None,
        }

    def to_json(self, output_path: Path) -> None:
        """Write metrics to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "metrics": self.metrics,
                    "summary": self.summary(),
                },
                f,
                indent=2,
            )


class profile_stage:
    """Context manager for profiling a stage."""

    def __init__(self, metrics: PerformanceMetrics, stage: str, **extra: Any):
        """
        Initialize profiler.

        Args:
            metrics: PerformanceMetrics instance
            stage: Stage name
            **extra: Additional metadata
        """
        self.metrics = metrics
        self.stage = stage
        self.extra = extra
        self.start_time: float = 0

    def __enter__(self) -> profile_stage:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        elapsed = time.perf_counter() - self.start_time
        self.metrics.record(self.stage, elapsed, **self.extra)


def memoize(func: F) -> F:
    """
    Simple memoization decorator.

    Caches results in memory based on argument hash.

    Args:
        func: Function to memoize

    Returns:
        Memoized function
    """
    cache: dict[str, Any] = {}

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper  # type: ignore


def chunked(items: list[Any], chunk_size: int) -> list[list[Any]]:
    """
    Split list into chunks.

    Args:
        items: List to split
        chunk_size: Maximum chunk size

    Returns:
        List of chunks
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
