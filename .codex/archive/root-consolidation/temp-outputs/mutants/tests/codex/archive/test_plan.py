"""
Tests for codex.archive.plan module.

This module contains tests for archive planning functionality.
"""

from pathlib import Path


class TestPlanEntry:
    """Tests for PlanEntry dataclass."""

    def test_basic_creation(self):
        """Test PlanEntry basic creation."""
        from codex.archive.plan import PlanEntry

        entry = PlanEntry(
            path="src/old_module.py", # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
            reason="dead",
            age_days=200,
            ref_count=0,
            coverage=0.0,
            score=0.9,
            commit_sha="abc123def456",
            mime="text/x-python",
            lang="python",
            tags=["deprecated"],
            size_bytes=1024,
            sloc=50,
        )

        assert entry.path == "src/old_module.py", "path is not valid"
        assert entry.reason == "dead", "reason is not valid"
        assert entry.age_days == 200, "age_days is not valid"
        assert entry.ref_count == 0, "Count must be greater than zero"
        assert entry.coverage == 0.0, "coverage is not valid"
        assert entry.score == 0.9, "score is not valid"
        assert entry.commit_sha == "abc123def456", "commit_sha is not valid"
        assert entry.mime == "text/x-python", "mime is not valid"
        assert entry.lang == "python", "lang is not valid"
        assert "deprecated" in entry.tags, "Condition must be true"
        assert entry.size_bytes == 1024, "size_bytes is not valid"
        assert entry.sloc == 50, "sloc is not valid"


class TestHasDeprecationTag:
    """Tests for _has_deprecation_tag function."""

    def test_deprecated_keyword(self, tmp_path):
        """Test detecting DEPRECATED keyword."""
        from codex.archive.plan import _has_deprecation_tag

        file_path = tmp_path / "test.py"
        file_path.write_text("# DEPRECATED: Do not use")

        result = _has_deprecation_tag(file_path)

        assert result is True, "Result must not be empty"

    def test_legacy_keyword(self, tmp_path):
        """Test detecting LEGACY keyword."""
        from codex.archive.plan import _has_deprecation_tag

        file_path = tmp_path / "test.py"
        file_path.write_text("# This is LEGACY code")

        result = _has_deprecation_tag(file_path)

        assert result is True, "Result must not be empty"

    def test_prune_me_keyword(self, tmp_path):
        """Test detecting PRUNE_ME keyword."""
        from codex.archive.plan import _has_deprecation_tag

        file_path = tmp_path / "test.py"
        file_path.write_text("# PRUNE_ME after migration")

        result = _has_deprecation_tag(file_path)

        assert result is True, "Result must not be empty"

    def test_no_deprecation(self, tmp_path):
        """Test file without deprecation markers."""
        from codex.archive.plan import _has_deprecation_tag

        file_path = tmp_path / "test.py"
        file_path.write_text("def foo(): pass")

        result = _has_deprecation_tag(file_path)

        assert result is False, "Result must not be empty"

    def test_nonexistent_file(self, tmp_path):
        """Test with nonexistent file."""
        from codex.archive.plan import _has_deprecation_tag

        file_path = tmp_path / "nonexistent.py"

        result = _has_deprecation_tag(file_path)

        assert result is False, "Result must not be empty"


class TestInExcludes:
    """Tests for _in_excludes function."""

    def test_matching_pattern(self):
        """Test file matching exclude pattern."""
        from codex.archive.plan import _in_excludes

        path = Path("src/__pycache__/module.pyc")
        excludes = ["*/__pycache__/*"]

        result = _in_excludes(path, excludes)

        assert result is True, "Result must not be empty"

    def test_not_matching(self):
        """Test file not matching exclude pattern."""
        from codex.archive.plan import _in_excludes

        path = Path("src/module.py")
        excludes = ["*/__pycache__/*"]

        result = _in_excludes(path, excludes)

        assert result is False, "Result must not be empty"

    def test_multiple_patterns(self):
        """Test multiple exclude patterns."""
        from codex.archive.plan import _in_excludes

        path = Path("node_modules/package.json")
        excludes = ["*.pyc", "node_modules/*", "*.log"]

        result = _in_excludes(path, excludes)

        assert result is True, "Result must not be empty"

    def test_empty_excludes(self):
        """Test with empty exclude list."""
        from codex.archive.plan import _in_excludes

        path = Path("any/file.py")
        excludes = []

        result = _in_excludes(path, excludes)

        assert result is False, "Result must not be empty"


class TestDeprecationPattern:
    """Tests for DEPRECATION_PAT constant."""

    def test_pattern_exists(self):
        """Test DEPRECATION_PAT constant exists."""
        from codex.archive.plan import DEPRECATION_PAT

        assert DEPRECATION_PAT is not None, "DEPRECATION_PAT must be initialized"

    def test_pattern_matches_deprecated(self):
        """Test pattern matches DEPRECATED."""
        from codex.archive.plan import DEPRECATION_PAT

        assert DEPRECATION_PAT.search("DEPRECATED"), "Condition must be true"
        assert DEPRECATION_PAT.search("deprecated"), "Condition must be true"

    def test_pattern_matches_legacy(self):
        """Test pattern matches LEGACY."""
        from codex.archive.plan import DEPRECATION_PAT

        assert DEPRECATION_PAT.search("LEGACY"), "Condition must be true"
        assert DEPRECATION_PAT.search("legacy"), "Condition must be true"


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.archive.plan import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.archive.plan", "name is not valid"
