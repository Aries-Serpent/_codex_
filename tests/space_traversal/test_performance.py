"""Tests for performance module (v1.5.5)."""
from __future__ import annotations

import json
import time
from pathlib import Path


def test_timed_decorator():
    """Test function timing decorator."""
    from scripts.space_traversal.performance import timed

    @timed
    def slow_function():
        time.sleep(0.1)
        return 42

    result = slow_function()
    assert result == 42


def test_file_cache_basic(tmp_path: Path):
    """Test basic cache operations."""
    from scripts.space_traversal.performance import FileCache

    cache = FileCache(tmp_path / "cache")

    # Set and get
    cache.set("key1", {"data": "value"})
    result = cache.get("key1")
    assert result == {"data": "value"}

    # Miss
    result = cache.get("nonexistent")
    assert result is None


def test_file_cache_expiry(tmp_path: Path):
    """Test cache TTL expiry."""
    from scripts.space_traversal.performance import FileCache

    cache = FileCache(tmp_path / "cache")

    # Set with very short TTL (1 second)
    cache.set("key1", "value", ttl_seconds=1)
    
    # Should still be valid
    result = cache.get("key1")
    assert result == "value"
    
    # Wait for expiry
    time.sleep(1.1)
    result = cache.get("key1")
    assert result is None


def test_file_cache_invalidate(tmp_path: Path):
    """Test cache invalidation."""
    from scripts.space_traversal.performance import FileCache

    cache = FileCache(tmp_path / "cache")

    cache.set("key1", "value")
    assert cache.get("key1") == "value"

    assert cache.invalidate("key1") is True
    assert cache.get("key1") is None
    assert cache.invalidate("key1") is False  # Already gone


def test_file_cache_clear(tmp_path: Path):
    """Test clearing entire cache."""
    from scripts.space_traversal.performance import FileCache

    cache = FileCache(tmp_path / "cache")

    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    count = cache.clear()
    assert count == 3
    assert cache.get("key1") is None
    assert cache.get("key2") is None


def test_file_cache_cleanup_expired(tmp_path: Path):
    """Test cleanup of expired entries."""
    from scripts.space_traversal.performance import FileCache

    cache = FileCache(tmp_path / "cache")

    # Set one with short TTL (1 second) and one with long TTL
    cache.set("expired", "old", ttl_seconds=1)
    cache.set("valid", "new", ttl_seconds=3600)

    # Wait for expiry
    time.sleep(1.1)

    count = cache.cleanup_expired()
    assert count == 1
    assert cache.get("valid") == "new"


def test_batch_file_read(tmp_path: Path):
    """Test batch file reading."""
    from scripts.space_traversal.performance import batch_file_read

    # Create test files
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.txt").write_text("content2")
    (tmp_path / "file3.txt").write_text("content3")

    paths = [
        tmp_path / "file1.txt",
        tmp_path / "file2.txt",
        tmp_path / "file3.txt",
        tmp_path / "nonexistent.txt",  # Should be skipped
    ]

    results = batch_file_read(paths)

    assert len(results) == 3
    assert results[str(tmp_path / "file1.txt")] == "content1"
    assert results[str(tmp_path / "file2.txt")] == "content2"


def test_batch_file_read_size_limit(tmp_path: Path):
    """Test batch file read respects size limit."""
    from scripts.space_traversal.performance import batch_file_read

    # Create small and large files
    (tmp_path / "small.txt").write_text("small")
    (tmp_path / "large.txt").write_text("x" * 1000)

    paths = [tmp_path / "small.txt", tmp_path / "large.txt"]

    # With small max_size, large file should be skipped
    results = batch_file_read(paths, max_size=100)

    assert len(results) == 1
    assert str(tmp_path / "small.txt") in results


def test_performance_metrics():
    """Test PerformanceMetrics collection."""
    from scripts.space_traversal.performance import PerformanceMetrics

    metrics = PerformanceMetrics()

    metrics.start_stage("stage1")
    time.sleep(0.1)
    metrics.end_stage()

    metrics.start_stage("stage2")
    time.sleep(0.05)
    metrics.end_stage(extra="data")

    summary = metrics.summary()

    assert summary["count"] == 2
    assert "stage1" in summary["stages"]
    assert "stage2" in summary["stages"]
    assert summary["total_seconds"] > 0.1


def test_performance_metrics_record():
    """Test direct metric recording."""
    from scripts.space_traversal.performance import PerformanceMetrics

    metrics = PerformanceMetrics()

    metrics.record("stage1", 1.5)
    metrics.record("stage2", 2.0)

    summary = metrics.summary()

    assert summary["stages"]["stage1"] == 1.5
    assert summary["stages"]["stage2"] == 2.0
    assert summary["total_seconds"] == 3.5


def test_performance_metrics_to_json(tmp_path: Path):
    """Test JSON export of metrics."""
    from scripts.space_traversal.performance import PerformanceMetrics

    metrics = PerformanceMetrics()
    metrics.record("stage1", 1.0)
    metrics.record("stage2", 2.0)

    output_path = tmp_path / "metrics.json"
    metrics.to_json(output_path)

    assert output_path.exists()

    data = json.loads(output_path.read_text())
    assert "metrics" in data
    assert "summary" in data
    assert len(data["metrics"]) == 2


def test_profile_stage_context_manager():
    """Test profile_stage context manager."""
    from scripts.space_traversal.performance import PerformanceMetrics, profile_stage

    metrics = PerformanceMetrics()

    with profile_stage(metrics, "my_stage"):
        time.sleep(0.05)

    summary = metrics.summary()
    assert "my_stage" in summary["stages"]
    assert summary["stages"]["my_stage"] >= 0.05


def test_memoize():
    """Test memoization decorator."""
    from scripts.space_traversal.performance import memoize

    call_count = [0]

    @memoize
    def expensive_function(x, y):
        call_count[0] += 1
        return x + y

    # First call
    result1 = expensive_function(1, 2)
    assert result1 == 3
    assert call_count[0] == 1

    # Second call with same args - should use cache
    result2 = expensive_function(1, 2)
    assert result2 == 3
    assert call_count[0] == 1  # No new call

    # Call with different args
    result3 = expensive_function(2, 3)
    assert result3 == 5
    assert call_count[0] == 2


def test_chunked():
    """Test list chunking utility."""
    from scripts.space_traversal.performance import chunked

    items = list(range(10))

    chunks = chunked(items, 3)
    assert len(chunks) == 4
    assert chunks[0] == [0, 1, 2]
    assert chunks[1] == [3, 4, 5]
    assert chunks[2] == [6, 7, 8]
    assert chunks[3] == [9]

    # Single chunk
    chunks = chunked(items, 20)
    assert len(chunks) == 1
    assert chunks[0] == items


def test_performance_metrics_empty():
    """Test metrics with no data."""
    from scripts.space_traversal.performance import PerformanceMetrics

    metrics = PerformanceMetrics()
    summary = metrics.summary()

    assert summary["total_seconds"] == 0
    assert summary["count"] == 0
    assert summary["stages"] == {}
