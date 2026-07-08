"""
Tests for codex.archive.batch module.

This module contains tests for batch restoration utilities.
"""

import tempfile
from pathlib import Path

import pytest


class TestBatchItem:
    """Tests for BatchItem dataclass."""

    def test_basic_creation(self):
        """Test BatchItem basic creation."""
        from codex.archive.batch import BatchItem

        item = BatchItem(tombstone="ts_123", output=Path(os.path.join(tempfile.gettempdir(), "output")), actor="user@example.com")

        assert item.tombstone == "ts_123", "Item must not be empty"
        assert item.output == Path(os.path.join(tempfile.gettempdir(), "output")), "Item must not be empty"
        assert item.actor == "user@example.com", "Item must not be empty"

    def test_from_dict_valid(self, tmp_path):
        """Test BatchItem.from_dict with valid data."""
        from codex.archive.batch import BatchItem

        payload = {"tombstone": "ts_001", "output": "output/path", "actor": "test_user"}

        item = BatchItem.from_dict(payload, manifest_dir=tmp_path, default_actor="default")

        assert item.tombstone == "ts_001", "Item must not be empty"
        assert item.actor == "test_user", "Item must not be empty"

    def test_from_dict_default_actor(self, tmp_path):
        """Test BatchItem.from_dict uses default actor."""
        from codex.archive.batch import BatchItem

        payload = {
            "tombstone": "ts_001",
            "output": "output/path",
            # No actor provided
        }

        item = BatchItem.from_dict(payload, manifest_dir=tmp_path, default_actor="default_user")

        assert item.actor == "default_user", "Item must not be empty"

    def test_from_dict_missing_tombstone(self, tmp_path):
        """Test BatchItem.from_dict raises on missing tombstone."""
        from codex.archive.batch import BatchItem

        payload = {"output": "output/path", "actor": "user"}

        with pytest.raises(ValueError, match="tombstone"):
            BatchItem.from_dict(payload, manifest_dir=tmp_path, default_actor="default")

    def test_from_dict_missing_output(self, tmp_path):
        """Test BatchItem.from_dict raises on missing output."""
        from codex.archive.batch import BatchItem

        payload = {"tombstone": "ts_001", "actor": "user"}

        with pytest.raises(ValueError, match="output"):
            BatchItem.from_dict(payload, manifest_dir=tmp_path, default_actor="default")

    def test_from_dict_empty_actor(self, tmp_path):
        """Test BatchItem.from_dict raises on empty actor."""
        from codex.archive.batch import BatchItem

        payload = {"tombstone": "ts_001", "output": "output/path", "actor": ""}

        with pytest.raises(ValueError, match=r"Actor must be provided"):
            BatchItem.from_dict(
                payload, manifest_dir=tmp_path, default_actor=""  # Empty default too
            )

    def test_frozen(self):
        """Test BatchItem is frozen (immutable)."""
        from codex.archive.batch import BatchItem

        item = BatchItem(tombstone="ts", output=Path("/tmp"), actor="user")

        with pytest.raises(AttributeError):
            item.tombstone = "new_ts"


class TestBatchResult:
    """Tests for BatchResult dataclass."""

    def test_basic_creation(self):
        """Test BatchResult basic creation."""
        from codex.archive.batch import BatchResult

        result = BatchResult(
            total=10, succeeded=8, failed=2, results=[{"id": 1}, {"id": 2}], metrics=None
        )

        assert result.total == 10, "Result must not be empty"
        assert result.succeeded == 8, "Result must not be empty"
        assert result.failed == 2, "Result must not be empty"
        assert len(result.results) == 2, "Collection must not be empty"
        assert result.metrics is None, "Result must not be empty"

    def test_to_dict(self):
        """Test BatchResult.to_dict method."""
        from codex.archive.batch import BatchResult

        result = BatchResult(total=5, succeeded=3, failed=2, results=[], metrics=None)

        d = result.to_dict()

        assert d["total"] == 5, "Condition must be true"
        assert d["succeeded"] == 3, "Condition must be true"
        assert d["failed"] == 2, "Condition must be true"


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.archive.batch import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.archive.batch", "name is not valid"
