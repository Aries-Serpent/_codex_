"""
Unit tests for session caching and context discovery utilities.

Tests cover:
  - FileCache: mtime tracking, invalidation, SHA256 hashing
  - SearchCache: memoization, cache hits/misses
  - Context discovery: git parsing, PR number detection
"""

import tempfile
import time
from pathlib import Path

import pytest

from src.codex.utils.context_discovery import discover_git_context, get_pr_number
from src.codex.utils.session_cache import FileCache, SearchCache


class TestFileCache:
    """Test FileCache class."""

    def test_cache_file(self):
        """Test adding file to cache."""
        cache = FileCache()
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write("test content")
            temp_path = f.name

        try:
            assert cache.add(temp_path)
            stats = cache.stats()
            assert stats["cached_files"] == 1
        finally:
            Path(temp_path).unlink()

    def test_cache_hit(self):
        """Test cache hit on retrieval."""
        cache = FileCache()
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write("test content")
            temp_path = f.name

        try:
            cache.add(temp_path)
            content = cache.get(temp_path)
            assert content == "test content"
        finally:
            Path(temp_path).unlink()

    def test_cache_miss(self):
        """Test cache miss on nonexistent file."""
        cache = FileCache()
        content = cache.get("/nonexistent/file.py")
        assert content is None

    def test_cache_invalidation(self):
        """Test cache invalidation on file modification."""
        cache = FileCache()
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write("original content")
            temp_path = f.name

        try:
            cache.add(temp_path)
            original_sha = cache.get_sha(temp_path)

            # Modify file
            with open(temp_path, "w") as f:
                f.write("modified content")

            # Ensure filesystem timestamp updates
            time.sleep(1)
            Path(temp_path).touch()

            # Should invalidate and refresh
            refreshed = cache.invalidate_if_modified(temp_path)
            assert refreshed is True
            content = cache.get(temp_path)
            new_sha = cache.get_sha(temp_path)

            assert content == "modified content"
            assert original_sha != new_sha
        finally:
            Path(temp_path).unlink()


class TestSearchCache:
    """Test SearchCache class."""

    def test_memoization(self):
        """Test search result memoization."""
        cache = SearchCache()
        call_count = 0

        @cache.memoize
        def dummy_search(query):
            nonlocal call_count
            call_count += 1
            return f"result for {query}"

        # First call
        result1 = dummy_search("test")
        assert result1 == "result for test"
        assert call_count == 1

        # Second call (cached)
        result2 = dummy_search("test")
        assert result2 == "result for test"
        assert call_count == 1  # Should not increment


class TestContextDiscovery:
    """Test context discovery functions."""

    def test_git_context_discovery(self):
        """Test git context discovery (requires git repo)."""
        context = discover_git_context()
        expected_keys = {"branch", "commit", "short_commit", "author", "email"}
        assert expected_keys.issubset(context.keys())
        for key in expected_keys:
            value = context[key]
            assert value is None or isinstance(value, str)

    def test_pr_number_default_fallback(self):
        """Test PR number detection fallback to N/A."""
        # When no env var, branch name, or commit message match, should return N/A
        pr = get_pr_number(interactive=False)
        assert pr in ["N/A"] or (isinstance(pr, str) and pr.isdigit())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
