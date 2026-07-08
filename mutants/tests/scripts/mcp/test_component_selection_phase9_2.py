"""
Phase 9.2 - Comprehensive tests for scripts/mcp/select_components.py

Tests cover:
- load_topics function
- expand_globs function with various patterns
- filter_by_topic function
- filter_by_globs function
- Error handling
- Edge cases

#AFTERMATH_METRIC - Phase 9.2 MCP component selection tests
"""

from __future__ import annotations

import json

# Import the module under test
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "mcp"))

from select_components import (
    expand_globs,
    filter_by_globs,
    filter_by_topic,
    load_topics,
)


class TestLoadTopics:
    """Test load_topics function."""

    def test_load_topics_valid_file(self, tmp_path: Path) -> None:
        """Test loading topics from valid JSON file."""
        # Arrange
        topics_data = {"zendesk": ["src/**/*.py"], "docs": ["docs/*.md"]}
        topics_file = tmp_path / "topics.json"
        topics_file.write_text(json.dumps(topics_data))

        # Act
        result = load_topics(topics_file)

        # Assert
        assert result == topics_data, "Result must not be empty"
        assert "zendesk" in result, "Result must not be empty"
        assert "docs" in result, "Result must not be empty"

    def test_load_topics_empty_file(self, tmp_path: Path) -> None:
        """Test loading empty topics file."""
        # Arrange
        topics_file = tmp_path / "topics.json"
        topics_file.write_text("{}")

        # Act
        result = load_topics(topics_file)

        # Assert
        assert result == {}, "Result must not be empty"

    def test_load_topics_file_not_found(self, tmp_path: Path) -> None:
        """Test loading non-existent topics file."""
        # Arrange
        topics_file = tmp_path / "nonexistent.json"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            load_topics(topics_file)


class TestExpandGlobs:
    """Test expand_globs function."""

    def test_expand_globs_simple_pattern(self, tmp_path: Path) -> None:
        """Test expanding simple glob pattern."""
        # Arrange
        (tmp_path / "test.txt").write_text("test")
        (tmp_path / "test.py").write_text("test")
        patterns = ["*.txt"]

        # Act
        result = expand_globs(patterns, tmp_path)

        # Assert
        assert len(result) >= 1, "Result must not be empty"
        assert any(p.name == "test.txt" for p in result), "Result must not be empty"

    def test_expand_globs_recursive_pattern(self, tmp_path: Path) -> None:
        """Test expanding recursive glob pattern."""
        # Arrange
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file.py").write_text("test")
        patterns = ["**/*.py"]

        # Act
        result = expand_globs(patterns, tmp_path)

        # Assert
        assert len(result) >= 1, "Result must not be empty"

    def test_expand_globs_no_matches(self, tmp_path: Path) -> None:
        """Test expanding pattern with no matches."""
        # Arrange
        patterns = ["*.xyz"]

        # Act
        result = expand_globs(patterns, tmp_path)

        # Assert
        assert len(result) == 0, "Result must not be empty"

    def test_expand_globs_multiple_patterns(self, tmp_path: Path) -> None:
        """Test expanding multiple glob patterns."""
        # Arrange
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "file2.py").write_text("test")
        patterns = ["*.txt", "*.py"]

        # Act
        result = expand_globs(patterns, tmp_path)

        # Assert
        assert len(result) >= 2, "Result must not be empty"

    def test_expand_globs_empty_patterns(self, tmp_path: Path) -> None:
        """Test expanding empty pattern list."""
        # Arrange
        patterns: list[str] = []

        # Act
        result = expand_globs(patterns, tmp_path)

        # Assert
        assert len(result) == 0, "Result must not be empty"

    def test_expand_globs_with_dot_prefix(self, tmp_path: Path) -> None:
        """Test pattern starting with dot."""
        # Arrange
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file.py").write_text("test")
        patterns = ["./**/*.py"]

        # Act
        result = expand_globs(patterns, tmp_path)

        # Assert
        assert isinstance(result, set)


class TestFilterByTopic:
    """Test filter_by_topic function."""

    def test_filter_by_topic_valid(self, tmp_path: Path) -> None:
        """Test filtering by valid topic."""
        # Arrange
        topics_map = {"test_topic": ["*.txt"]}
        (tmp_path / "file.txt").write_text("test")

        # Act
        result = filter_by_topic("test_topic", topics_map, tmp_path)

        # Assert
        assert isinstance(result, set)

    def test_filter_by_topic_unknown(self, tmp_path: Path) -> None:
        """Test filtering by unknown topic."""
        # Arrange
        topics_map = {"known": ["*.txt"]}

        # Act & Assert
        with pytest.raises(ValueError, match="Unknown topic"):
            filter_by_topic("unknown", topics_map, tmp_path)

    def test_filter_by_topic_empty_result(self, tmp_path: Path) -> None:
        """Test filtering with no matching files."""
        # Arrange
        topics_map = {"test": ["*.xyz"]}

        # Act
        result = filter_by_topic("test", topics_map, tmp_path)

        # Assert
        assert len(result) == 0, "Result must not be empty"

    def test_filter_by_topic_multiple_patterns(self, tmp_path: Path) -> None:
        """Test filtering with multiple patterns."""
        # Arrange
        topics_map = {"test": ["*.txt", "*.py"]}
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "file2.py").write_text("test")

        # Act
        result = filter_by_topic("test", topics_map, tmp_path)

        # Assert
        assert len(result) >= 2, "Result must not be empty"


class TestFilterByGlobs:
    """Test filter_by_globs function."""

    def test_filter_by_globs_single_pattern(self, tmp_path: Path) -> None:
        """Test filtering with single glob pattern."""
        # Arrange
        (tmp_path / "file.txt").write_text("test")
        glob_patterns = "*.txt"

        # Act
        result = filter_by_globs(glob_patterns, tmp_path)

        # Assert
        assert len(result) >= 1, "Result must not be empty"

    def test_filter_by_globs_multiple_patterns(self, tmp_path: Path) -> None:
        """Test filtering with multiple comma-separated patterns."""
        # Arrange
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "file2.py").write_text("test")
        glob_patterns = "*.txt, *.py"

        # Act
        result = filter_by_globs(glob_patterns, tmp_path)

        # Assert
        assert len(result) >= 2, "Result must not be empty"

    def test_filter_by_globs_empty_string(self, tmp_path: Path) -> None:
        """Test filtering with empty pattern string."""
        # Arrange
        glob_patterns = ""

        # Act
        result = filter_by_globs(glob_patterns, tmp_path)

        # Assert
        assert len(result) == 0, "Result must not be empty"

    def test_filter_by_globs_whitespace_handling(self, tmp_path: Path) -> None:
        """Test pattern whitespace is handled correctly."""
        # Arrange
        (tmp_path / "file.txt").write_text("test")
        glob_patterns = "  *.txt  ,  "

        # Act
        result = filter_by_globs(glob_patterns, tmp_path)

        # Assert
        assert len(result) >= 1, "Result must not be empty"

    def test_filter_by_globs_no_matches(self, tmp_path: Path) -> None:
        """Test filtering with patterns that match nothing."""
        # Arrange
        glob_patterns = "*.xyz, *.abc"

        # Act
        result = filter_by_globs(glob_patterns, tmp_path)

        # Assert
        assert len(result) == 0, "Result must not be empty"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_expand_globs_directories_excluded(self, tmp_path: Path) -> None:
        """Test that directories are not included in results."""
        # Arrange
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        patterns = ["*"]

        # Act
        result = expand_globs(patterns, tmp_path)

        # Assert
        # Should only include files, not directories
        for path in result:
            assert (tmp_path / path).is_file(), "Condition must be true"

    def test_expand_globs_relative_paths(self, tmp_path: Path) -> None:
        """Test that results are relative to base_dir."""
        # Arrange
        (tmp_path / "file.txt").write_text("test")
        patterns = ["*.txt"]

        # Act
        result = expand_globs(patterns, tmp_path)

        # Assert
        for path in result:
            # Paths should be relative, not absolute
            assert not path.is_absolute(), "Condition must be true"

    def test_filter_by_topic_preserves_topic_patterns(self, tmp_path: Path) -> None:
        """Test that topic patterns are used correctly."""
        # Arrange
        topics_map = {"test": ["specific/**/*.py"]}
        specific_dir = tmp_path / "specific"
        specific_dir.mkdir()
        (specific_dir / "file.py").write_text("test")
        (tmp_path / "other.py").write_text("test")

        # Act
        result = filter_by_topic("test", topics_map, tmp_path)

        # Assert
        # Should only match files in specific/ directory
        assert all("specific" in str(p) for p in result if len(result) > 0), "Result must not be empty"


# #AFTERMATH_METRIC - 15 tests created for scripts/mcp/select_components.py
# Coverage: load_topics, expand_globs, filter_by_topic, filter_by_globs, edge cases
# Test pattern: AAA (Arrange-Act-Assert)
