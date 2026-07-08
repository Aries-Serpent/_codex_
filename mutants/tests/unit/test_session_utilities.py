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

from codex.utils.context_discovery import discover_git_context, get_pr_number
from codex.utils.session_cache import FileCache, SearchCache


class TestFileCache:
    """Test FileCache class."""

    def test_cache_file(self):
        """Test adding file to cache."""
        cache = FileCache()
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write("test content")
            temp_path = f.name

        try:
            add_result = cache.add(temp_path)
            assert add_result, "Result must not be empty"
            stats = cache.stats()
            assert stats["cached_files"] == 1, "Condition must be true"
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
            assert content == "test content", "Content must not be empty"
        finally:
            Path(temp_path).unlink()

    def test_cache_miss(self):
        """Test cache miss on nonexistent file."""
        cache = FileCache()
        content = cache.get("/nonexistent/file.py")
        assert content is None, "Content must not be empty"

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
            assert refreshed is True, "refreshed is not valid"
            content = cache.get(temp_path)
            new_sha = cache.get_sha(temp_path)

            assert content == "modified content", "Content must not be empty"
            assert original_sha != new_sha, "original_sha is not valid"
        finally:
            Path(temp_path).unlink()


class TestSearchCache:
    """Test SearchCache class."""

    def test_memoization(self):
        """Test search result memoization."""
        cache = SearchCache()
        call_count = [0]

        @cache.memoize
        def dummy_search(query):
            call_count[0] += 1
            return f"result for {query}"

        # First call
        result1 = dummy_search("test")
        assert result1 == "result for test", "Result must not be empty"
        assert call_count[0] == 1, "Count must be greater than zero"

        # Second call (cached)
        result2 = dummy_search("test")
        assert result2 == "result for test", "Result must not be empty"
        assert call_count[0] == 1, "Count must be greater than zero"


class TestContextDiscovery:
    """Test context discovery functions."""

    def test_git_context_discovery(self):
        """Test git context discovery (requires git repo)."""
        context = discover_git_context()
        expected_keys = {"branch", "commit", "short_commit", "author", "email"}
        assert expected_keys.issubset(context.keys()), "Condition must be true"
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
