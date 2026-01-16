"""
Tests for codex.archive.consolidate module.

This module contains tests for consolidation planning utilities.
"""

import pytest
from pathlib import Path


class TestSerialisePath:
    """Tests for _serialise_path function."""

    def test_relative_path(self, tmp_path):
        """Test serializing a relative path."""
        from codex.archive.consolidate import _serialise_path
        
        file_path = tmp_path / "src" / "module.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        
        result = _serialise_path(file_path, tmp_path)
        
        assert result == "src/module.py"

    def test_path_outside_root(self, tmp_path):
        """Test serializing a path outside root."""
        from codex.archive.consolidate import _serialise_path
        
        file_path = Path("/some/other/path.py")
        
        result = _serialise_path(file_path, tmp_path)
        
        # Should return full posix path
        assert "some/other/path.py" in result


class TestInExcludes:
    """Tests for _in_excludes function."""

    def test_matching_pattern(self):
        """Test file matching exclude pattern."""
        from codex.archive.consolidate import _in_excludes
        
        path = Path("src/__pycache__/module.pyc")
        patterns = ["*/__pycache__/*"]
        
        result = _in_excludes(path, patterns)
        
        assert result is True

    def test_not_matching(self):
        """Test file not matching pattern."""
        from codex.archive.consolidate import _in_excludes
        
        path = Path("src/module.py")
        patterns = ["*.pyc"]
        
        result = _in_excludes(path, patterns)
        
        assert result is False


class TestFreshness:
    """Tests for _freshness function."""

    def test_recent_file(self):
        """Test freshness for recently modified file."""
        from codex.archive.consolidate import _freshness
        import time
        
        now = time.time()
        mtime = now - (3 * 86400)  # 3 days ago
        
        result = _freshness(now, mtime)
        
        assert result == 1.0

    def test_week_old_file(self):
        """Test freshness for week-old file."""
        from codex.archive.consolidate import _freshness
        import time
        
        now = time.time()
        mtime = now - (15 * 86400)  # 15 days ago
        
        result = _freshness(now, mtime)
        
        assert result == 0.8

    def test_month_old_file(self):
        """Test freshness for month-old file."""
        from codex.archive.consolidate import _freshness
        import time
        
        now = time.time()
        mtime = now - (60 * 86400)  # 60 days ago
        
        result = _freshness(now, mtime)
        
        assert result == 0.5

    def test_old_file(self):
        """Test freshness for old file."""
        from codex.archive.consolidate import _freshness
        import time
        
        now = time.time()
        mtime = now - (400 * 86400)  # 400 days ago
        
        result = _freshness(now, mtime)
        
        assert result == 0.1


class TestPathFitness:
    """Tests for _path_fitness function."""

    def test_src_codex_path(self):
        """Test fitness for src/codex path."""
        from codex.archive.consolidate import _path_fitness
        
        result = _path_fitness("src/codex/module.py")
        
        assert result >= 0.5

    def test_legacy_path(self):
        """Test fitness penalty for legacy path."""
        from codex.archive.consolidate import _path_fitness
        
        result = _path_fitness("legacy/old_module.py")
        
        assert result == 0.0  # Penalty makes it 0

    def test_v2_path(self):
        """Test fitness bonus for v2 suffix."""
        from codex.archive.consolidate import _path_fitness
        
        result = _path_fitness("src/codex/module_v2.py")
        
        assert result >= 0.5

    def test_regular_path(self):
        """Test fitness for regular path."""
        from codex.archive.consolidate import _path_fitness
        
        result = _path_fitness("random/path.py")
        
        assert 0.0 <= result <= 1.0


class TestComplexityPenalty:
    """Tests for _complexity_penalty function."""

    def test_small_file(self):
        """Test penalty for small file."""
        from codex.archive.consolidate import _complexity_penalty
        
        result = _complexity_penalty(1024, 50)
        
        assert result < 0.1

    def test_large_file(self):
        """Test penalty for large file."""
        from codex.archive.consolidate import _complexity_penalty
        
        result = _complexity_penalty(256 * 1024, 1000)
        
        assert result >= 0.3

    def test_max_penalty(self):
        """Test penalty is capped at 0.4."""
        from codex.archive.consolidate import _complexity_penalty
        
        result = _complexity_penalty(1024 * 1024, 5000)
        
        assert result == 0.4


class TestUsageHeuristic:
    """Tests for _usage_heuristic function."""

    def test_legacy_path(self):
        """Test heuristic for legacy path."""
        from codex.archive.consolidate import _usage_heuristic
        
        result = _usage_heuristic(Path("legacy/old.py"))
        
        assert result == 0.1

    def test_regular_path(self):
        """Test heuristic for regular path."""
        from codex.archive.consolidate import _usage_heuristic
        
        result = _usage_heuristic(Path("src/module.py"))
        
        # Regular paths should have higher usage heuristic
        assert result >= 0.1


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.archive.consolidate import logger
        
        assert logger is not None
        assert logger.name == "codex.archive.consolidate"
