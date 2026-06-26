"""Tests for delta analysis."""

import tempfile

import pytest

from codex.ast.baseline import BaselineManager
from codex.ast.delta import DeltaAnalyzer, DeltaResult


def test_delta_result_summary():
    """Test DeltaResult summary."""
    result = DeltaResult(
        added=["a.py"],
        removed=["b.py"],
        modified=["c.py"],
        unchanged=["d.py", "e.py"],
    )
    summary = result.summary()
    assert "Added: 1" in summary, "Condition must be true"
    assert "Removed: 1" in summary, "Condition must be true"
    assert "Modified: 1" in summary, "Condition must be true"
    assert "Unchanged: 2" in summary, "Condition must be true"


def test_delta_result_has_changes():
    """Test DeltaResult has_changes."""
    result_with_changes = DeltaResult(added=["a.py"], removed=[], modified=[], unchanged=[])
    assert result_with_changes.has_changes(), "Result must not be empty"

    result_no_changes = DeltaResult(added=[], removed=[], modified=[], unchanged=["a.py"])
    assert not result_no_changes.has_changes(), "Result must not be empty"


def test_delta_result_total_changes():
    """Test DeltaResult total_changes."""
    result = DeltaResult(
        added=["a.py", "b.py"],
        removed=["c.py"],
        modified=["d.py", "e.py", "f.py"],
        unchanged=["g.py"],
    )
    assert result.total_changes() == 6, "Result must not be empty"

    result_empty = DeltaResult(added=[], removed=[], modified=[], unchanged=["x.py"])
    assert result_empty.total_changes() == 0, "Result must not be empty"


def test_detect_added_files():
    """Test detection of added files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BaselineManager(f"{tmpdir}/test.db")
        analyzer = DeltaAnalyzer(manager)

        # Empty baseline
        current = {"new.py": {"ast_hash": "abc123"}}

        result = analyzer.analyze(current)
        assert "new.py" in result.added, "Result must not be empty"
        assert len(result.removed) == 0, "Collection must not be empty"
        assert len(result.modified) == 0, "Collection must not be empty"


def test_detect_removed_files():
    """Test detection of removed files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BaselineManager(f"{tmpdir}/test.db")
        analyzer = DeltaAnalyzer(manager)

        # Save baseline
        manager.save_baseline("old.py", "abc123", 10, 1)

        # File no longer exists
        current = {}

        result = analyzer.analyze(current)
        assert "old.py" in result.removed, "Result must not be empty"


def test_detect_modified_files():
    """Test detection of modified files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BaselineManager(f"{tmpdir}/test.db")
        analyzer = DeltaAnalyzer(manager)

        # Save baseline
        manager.save_baseline("file.py", "abc123", 10, 1)

        # File modified (different hash)
        current = {"file.py": {"ast_hash": "def456"}}

        result = analyzer.analyze(current)
        assert "file.py" in result.modified, "Result must not be empty"


def test_detect_unchanged_files():
    """Test detection of unchanged files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BaselineManager(f"{tmpdir}/test.db")
        analyzer = DeltaAnalyzer(manager)

        # Save baseline
        manager.save_baseline("file.py", "abc123", 10, 1)

        # File unchanged (same hash)
        current = {"file.py": {"ast_hash": "abc123"}}

        result = analyzer.analyze(current)
        assert "file.py" in result.unchanged, "Result must not be empty"


def test_analyze_file():
    """Test single file analysis."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BaselineManager(f"{tmpdir}/test.db")
        analyzer = DeltaAnalyzer(manager)

        # New file
        assert analyzer.analyze_file("new.py", {"ast_hash": "abc"}) == "added"

        # Save baseline
        manager.save_baseline("existing.py", "abc123", 10, 1)

        # Modified file
        assert analyzer.analyze_file("existing.py", {"ast_hash": "def456"}) == "modified"

        # Unchanged file
        assert analyzer.analyze_file("existing.py", {"ast_hash": "abc123"}) == "unchanged"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
