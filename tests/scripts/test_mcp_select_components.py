"""
Test Mcp Select Components

Test module for mcp select components.
"""

#! /usr/bin/env python3
"""
Test suite for scripts/mcp/select_components.py
Tests component selection, glob expansion, and topic filtering
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts/mcp to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "mcp"))
from select_components import (
    expand_globs,
    filter_by_globs,
    filter_by_topic,
    load_topics,
)


@pytest.fixture
def temp_repo():
    """Create a temporary repository structure for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Create test file structure
        (base / "src").mkdir()
        (base / "src" / "main.py").write_text("# main")
        (base / "src" / "utils.py").write_text("# utils")

        (base / "tests").mkdir()
        (base / "tests" / "test_main.py").write_text("# test")

        (base / "docs").mkdir()
        (base / "docs" / "guide.md").write_text("# guide")
        (base / "docs" / "api").mkdir()
        (base / "docs" / "api" / "reference.md").write_text("# ref")

        (base / "scripts").mkdir()
        (base / "scripts" / "build.sh").write_text("#!/bin/bash")

        yield base


@pytest.fixture
def sample_topics():
    """Sample topics map for testing"""
    return {
        "python": ["src/**/*.py", "tests/**/*.py"],
        "docs": ["docs/**/*.md"],
        "scripts": ["scripts/**/*.sh"],
        "all": ["**/*.py", "**/*.md", "**/*.sh"],
    }


@pytest.fixture
def topics_file(temp_repo, sample_topics):
    """Create a topics.json file in temp directory"""
    topics_path = temp_repo / "topics.json"
    with open(topics_path, "w") as f:
        json.dump(sample_topics, f)
    return topics_path


class TestLoadTopics:
    """Tests for load_topics function"""

    def test_load_topics_valid_file(self, topics_file, sample_topics):
        """Test loading topics from valid JSON file"""
        topics = load_topics(topics_file)
        assert topics == sample_topics, "topics is not valid"
        assert "python" in topics, "Condition must be true"
        assert isinstance(topics["python"], list)

    def test_load_topics_missing_file(self, temp_repo):
        """Test error handling for missing topics file"""
        missing_file = temp_repo / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            load_topics(missing_file)

    def test_load_topics_invalid_json(self, temp_repo):
        """Test error handling for invalid JSON"""
        invalid_file = temp_repo / "invalid.json"
        invalid_file.write_text("{invalid json}")
        with pytest.raises(json.JSONDecodeError):
            load_topics(invalid_file)

    def test_load_topics_empty_file(self, temp_repo):
        """Test loading empty topics file"""
        empty_file = temp_repo / "empty.json"
        empty_file.write_text("{}")
        topics = load_topics(empty_file)
        assert topics == {}, "topics is not valid"


class TestExpandGlobs:
    """Tests for expand_globs function"""

    def test_expand_simple_glob(self, temp_repo):
        """Test expanding simple glob pattern"""
        patterns = ["src/*.py"]
        files = expand_globs(patterns, temp_repo)

        assert len(files) == 2, "Files must not be empty"
        assert Path("src/main.py") in files, "Condition must be true"
        assert Path("src/utils.py") in files, "Condition must be true"

    def test_expand_recursive_glob(self, temp_repo):
        """Test expanding recursive ** pattern"""
        patterns = ["**/*.py"]
        files = expand_globs(patterns, temp_repo)

        assert len(files) == 3, "Files must not be empty"
        assert Path("src/main.py") in files, "Condition must be true"
        assert Path("src/utils.py") in files, "Condition must be true"
        assert Path("tests/test_main.py") in files, "Condition must be true"

    def test_expand_specific_recursive_glob(self, temp_repo):
        """Test expanding specific directory with **"""
        patterns = ["docs/**/*.md"]
        files = expand_globs(patterns, temp_repo)

        assert len(files) == 2, "Files must not be empty"
        assert Path("docs/guide.md") in files, "Condition must be true"
        assert Path("docs/api/reference.md") in files, "Condition must be true"

    def test_expand_multiple_patterns(self, temp_repo):
        """Test expanding multiple glob patterns"""
        patterns = ["src/*.py", "tests/*.py"]
        files = expand_globs(patterns, temp_repo)

        assert len(files) == 3, "Files must not be empty"

    def test_expand_no_matches(self, temp_repo):
        """Test glob pattern with no matches"""
        patterns = ["nonexistent/**/*.txt"]
        files = expand_globs(patterns, temp_repo)

        assert len(files) == 0, "Files must not be empty"

    def test_expand_glob_with_dot_prefix(self, temp_repo):
        """Test glob pattern starting with ./"""
        patterns = ["./src/**/*.py"]
        files = expand_globs(patterns, temp_repo)

        assert len(files) == 2, "Files must not be empty"

    def test_expand_glob_edge_case_star_star_only(self, temp_repo):
        """Test edge case with ** not as separate segment - should raise ValueError"""
        patterns = ["src/**.py"]  # ** not as separate path segment - invalid pattern

        # Python's pathlib correctly raises ValueError for invalid ** usage
        with pytest.raises(ValueError, match="Invalid pattern"):
            expand_globs(patterns, temp_repo)

    def test_expand_glob_directories_excluded(self, temp_repo):
        """Test that directories are excluded, only files returned"""
        patterns = ["**/*"]
        files = expand_globs(patterns, temp_repo)

        # Should only include files, not directories
        for f in files:
            assert (temp_repo / f).is_file(), "Condition must be true"


class TestFilterByTopic:
    """Tests for filter_by_topic function"""

    def test_filter_valid_topic(self, temp_repo, sample_topics):
        """Test filtering by valid topic"""
        files = filter_by_topic("python", sample_topics, temp_repo)

        assert len(files) == 3, "Files must not be empty"
        assert all(str(f).endswith(".py") for f in files), "Condition must be true"

    def test_filter_unknown_topic(self, temp_repo, sample_topics):
        """Test error handling for unknown topic"""
        with pytest.raises(ValueError, match="Unknown topic"):
            filter_by_topic("nonexistent", sample_topics, temp_repo)

    def test_filter_docs_topic(self, temp_repo, sample_topics):
        """Test filtering docs topic"""
        files = filter_by_topic("docs", sample_topics, temp_repo)

        assert len(files) == 2, "Files must not be empty"
        assert all(str(f).endswith(".md") for f in files), "Condition must be true"

    def test_filter_all_topic(self, temp_repo, sample_topics):
        """Test filtering 'all' topic"""
        files = filter_by_topic("all", sample_topics, temp_repo)

        # Should include .py, .md, and .sh files
        assert len(files) >= 6, "Files must not be empty"


class TestFilterByGlobs:
    """Tests for filter_by_globs function"""

    def test_filter_single_glob(self, temp_repo):
        """Test filtering by single glob pattern"""
        files = filter_by_globs("src/**/*.py", temp_repo)

        assert len(files) == 2, "Files must not be empty"

    def test_filter_multiple_globs_comma_separated(self, temp_repo):
        """Test filtering by comma-separated glob patterns"""
        files = filter_by_globs("src/**/*.py, tests/**/*.py", temp_repo)

        assert len(files) == 3, "Files must not be empty"

    def test_filter_globs_with_whitespace(self, temp_repo):
        """Test glob patterns with extra whitespace"""
        files = filter_by_globs("  src/**/*.py  ,  tests/**/*.py  ", temp_repo)

        assert len(files) == 3, "Files must not be empty"

    def test_filter_empty_glob_string(self, temp_repo):
        """Test empty glob string"""
        files = filter_by_globs("", temp_repo)

        assert len(files) == 0, "Files must not be empty"

    def test_filter_globs_with_empty_elements(self, temp_repo):
        """Test glob string with empty comma-separated elements"""
        files = filter_by_globs("src/**/*.py,,, tests/**/*.py", temp_repo)

        # Should ignore empty elements
        assert len(files) == 3, "Files must not be empty"


class TestEdgeCases:
    """Tests for edge cases and error conditions"""

    def test_symlink_handling(self, temp_repo):
        """Test handling of symbolic links"""
        # Create a file and a symlink to it
        real_file = temp_repo / "real.py"
        real_file.write_text("# real")

        symlink_file = temp_repo / "link.py"
        try:
            symlink_file.symlink_to(real_file)

            files = expand_globs(["*.py"], temp_repo)

            # Both real file and symlink should be included (symlink is also a file)
            assert len(files) >= 1, "Files must not be empty"
        except OSError:
            # Skip if symlinks not supported
            pytest.skip("Symlinks not supported on this platform")

    def test_large_file_handling(self, temp_repo):
        """Test handling of large files (metadata only)"""
        large_file = temp_repo / "large.py"
        # Create file with large content
        large_file.write_text("# " + "x" * 1000000)  # 1MB

        files = expand_globs(["large.py"], temp_repo)

        assert len(files) == 1, "Files must not be empty"
        assert Path("large.py") in files, "Condition must be true"

    def test_special_characters_in_filenames(self, temp_repo):
        """Test handling of special characters in filenames"""
        special_file = temp_repo / "file with spaces.py"
        special_file.write_text("# special")

        files = expand_globs(["file*.py"], temp_repo)

        assert len(files) == 1, "Files must not be empty"

    def test_deeply_nested_directories(self, temp_repo):
        """Test handling of deeply nested directory structures"""
        deep_path = temp_repo / "a" / "b" / "c" / "d" / "e"
        deep_path.mkdir(parents=True)
        (deep_path / "deep.py").write_text("# deep")

        files = expand_globs(["**/*.py"], temp_repo)

        assert Path("a/b/c/d/e/deep.py") in files, "Condition must be true"

    def test_empty_directory_handling(self, temp_repo):
        """Test handling of empty directories"""
        empty_dir = temp_repo / "empty"
        empty_dir.mkdir()

        files = expand_globs(["empty/**/*.py"], temp_repo)

        assert len(files) == 0, "Files must not be empty"

    def test_path_traversal_safety(self, temp_repo):
        """Test that path traversal attempts are handled safely"""
        # Try to access parent directory
        files = expand_globs(["../*.py"], temp_repo)

        # Should not traverse outside base_dir
        # All returned paths should be relative to base_dir
        for f in files:
            assert not str(f).startswith(".."), "Condition must be true"


# Run tests with: python -m pytest tests/scripts/test_mcp_select_components.py -v
