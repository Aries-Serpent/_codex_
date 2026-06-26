"""Tests for baseline management."""

import tempfile
from pathlib import Path

import pytest

from codex.ast.baseline import BaselineManager


def test_baseline_init():
    """Test baseline database initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        BaselineManager(str(db_path))
        assert db_path.exists(), "Condition must be true"


def test_save_and_retrieve():
    """Test saving and retrieving baselines."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BaselineManager(f"{tmpdir}/test.db")

        # Save baseline
        manager.save_baseline("test.py", "abc123", 50, 10, {"author": "test"})

        # Retrieve baseline
        baseline = manager.get_baseline("test.py")
        assert baseline is not None, "baseline must be initialized"
        assert baseline["ast_hash"] == "abc123", "Condition must be true"
        assert baseline["node_count"] == 50, "Count must be greater than zero"
        assert baseline["complexity"] == 10, "Condition must be true"
        assert baseline["metadata"]["author"] == "test", "Data must not be empty"


def test_update_baseline():
    """Test updating existing baseline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BaselineManager(f"{tmpdir}/test.db")

        # Save initial baseline
        manager.save_baseline("test.py", "abc123", 50, 10)

        # Update baseline
        manager.save_baseline("test.py", "def456", 60, 12)

        # Check version incremented
        baseline = manager.get_baseline("test.py")
        assert baseline["ast_hash"] == "def456", "Condition must be true"
        assert baseline["version"] == 2, "Condition must be true"


def test_list_baselines():
    """Test listing all baselines."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BaselineManager(f"{tmpdir}/test.db")

        manager.save_baseline("file1.py", "hash1", 10, 1)
        manager.save_baseline("file2.py", "hash2", 20, 2)

        baselines = manager.list_baselines()
        assert len(baselines) == 2, "Baselines must not be empty"


def test_delete_baseline():
    """Test deleting a baseline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BaselineManager(f"{tmpdir}/test.db")

        manager.save_baseline("test.py", "abc123", 50, 10)
        manager.delete_baseline("test.py")

        baseline = manager.get_baseline("test.py")
        assert baseline is None, "baseline is not valid"


def test_clear_all():
    """Test clearing all baselines."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BaselineManager(f"{tmpdir}/test.db")

        manager.save_baseline("file1.py", "hash1", 10, 1)
        manager.save_baseline("file2.py", "hash2", 20, 2)
        manager.clear_all()

        baselines = manager.list_baselines()
        assert len(baselines) == 0, "Baselines must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
