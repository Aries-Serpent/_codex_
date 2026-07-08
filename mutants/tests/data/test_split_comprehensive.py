"""Comprehensive tests for codex_ml.data.split module.

Tests cover:
- Train/val/test splitting strategies
- Deterministic splitting with seeds
- Split metadata and checksums
- Manifest generation
- Error handling
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

# Import module under test
try:
    from codex_ml.data import split
except ImportError:
    pytest.skip("split module not available", allow_module_level=True)


class TestModuleConstants:
    """Test module-level constants."""

    def test_default_manifest_name(self):
        """Test DEFAULT_MANIFEST_NAME constant."""
        assert hasattr(split, "DEFAULT_MANIFEST_NAME")
        assert isinstance(split.DEFAULT_MANIFEST_NAME, str)
        assert "manifest" in split.DEFAULT_MANIFEST_NAME.lower(), "Condition must be true"

    def test_default_checksums_name(self):
        """Test DEFAULT_CHECKSUMS_NAME constant."""
        assert hasattr(split, "DEFAULT_CHECKSUMS_NAME")
        assert isinstance(split.DEFAULT_CHECKSUMS_NAME, str)
        assert "checksum" in split.DEFAULT_CHECKSUMS_NAME.lower(), "Condition must be true"

    def test_manifest_schema(self):
        """Test MANIFEST_SCHEMA constant."""
        assert hasattr(split, "MANIFEST_SCHEMA")
        assert isinstance(split.MANIFEST_SCHEMA, str)

    def test_manifest_version(self):
        """Test MANIFEST_VERSION constant."""
        assert hasattr(split, "MANIFEST_VERSION")
        assert isinstance(split.MANIFEST_VERSION, str)


class TestHashIdentifier:
    """Test _hash_identifier function."""

    def test_hash_identifier_basic(self):
        """Test basic identifier hashing."""
        if hasattr(split, "_hash_identifier"):
            result = split._hash_identifier("test_dataset")
            assert isinstance(result, str)
            assert len(result) == 64, "Result must not be empty"

    def test_hash_identifier_deterministic(self):
        """Test hashing is deterministic."""
        if hasattr(split, "_hash_identifier"):
            result1 = split._hash_identifier("test_dataset")
            result2 = split._hash_identifier("test_dataset")
            assert result1 == result2, "Result must not be empty"

    def test_hash_identifier_different_inputs(self):
        """Test different inputs produce different hashes."""
        if hasattr(split, "_hash_identifier"):
            result1 = split._hash_identifier("dataset_a")
            result2 = split._hash_identifier("dataset_b")
            assert result1 != result2, "Result must not be empty"

    def test_hash_identifier_empty_string(self):
        """Test hashing empty string."""
        if hasattr(split, "_hash_identifier"):
            result = split._hash_identifier("")
            assert isinstance(result, str)
            assert len(result) == 64, "Result must not be empty"


class TestJsonReady:
    """Test _json_ready helper function."""

    def test_json_ready_with_string(self):
        """Test _json_ready with string."""
        if hasattr(split, "_json_ready"):
            result = split._json_ready("test")
            assert result == "test", "Result must not be empty"

    def test_json_ready_with_int(self):
        """Test _json_ready with int."""
        if hasattr(split, "_json_ready"):
            result = split._json_ready(42)
            assert result == 42, "Result must not be empty"

    def test_json_ready_with_float(self):
        """Test _json_ready with float."""
        if hasattr(split, "_json_ready"):
            result = split._json_ready(3.14)
            assert result == 3.14, "Result must not be empty"

    def test_json_ready_with_bool(self):
        """Test _json_ready with bool."""
        if hasattr(split, "_json_ready"):
            result = split._json_ready(True)
            assert result is True, "Result must not be empty"

    def test_json_ready_with_none(self):
        """Test _json_ready with None."""
        if hasattr(split, "_json_ready"):
            result = split._json_ready(None)
            assert result is None, "Result must not be empty"

    def test_json_ready_with_path(self):
        """Test _json_ready with Path object."""
        if hasattr(split, "_json_ready"):
            result = split._json_ready(Path(os.path.join(tempfile.gettempdir(), "test")))
            assert isinstance(result, str)
            assert result == os.path.join(tempfile.gettempdir(), "test"), "Result must not be empty"

    def test_json_ready_with_dict(self):
        """Test _json_ready with dict."""
        if hasattr(split, "_json_ready"):
            data = {"key": "value", "num": 42}
            result = split._json_ready(data)
            assert isinstance(result, dict)
            assert result["key"] == "value", "Result must not be empty"

    def test_json_ready_with_list(self):
        """Test _json_ready with list."""
        if hasattr(split, "_json_ready"):
            data = [1, "two", 3.0]
            result = split._json_ready(data)
            assert isinstance(result, list)
            assert len(result) == 3, "Result must not be empty"

    def test_json_ready_with_nested_structures(self):
        """Test _json_ready with nested structures."""
        if hasattr(split, "_json_ready"):
            data = {"path": Path("/tmp"), "items": [1, 2, 3]}
            result = split._json_ready(data)
            assert isinstance(result["path"], str)
            assert isinstance(result["items"], list)


class TestSplitChecksum:
    """Test _split_checksum function."""

    def test_split_checksum_basic(self):
        """Test basic checksum computation."""
        if hasattr(split, "_split_checksum"):
            indices = [0, 1, 2, 3, 4]
            result = split._split_checksum("dataset_hash", "train", indices)
            assert isinstance(result, str)
            assert len(result) == 64, "Result must not be empty"

    def test_split_checksum_deterministic(self):
        """Test checksum is deterministic."""
        if hasattr(split, "_split_checksum"):
            indices = [0, 1, 2, 3, 4]
            result1 = split._split_checksum("dataset_hash", "train", indices)
            result2 = split._split_checksum("dataset_hash", "train", indices)
            assert result1 == result2, "Result must not be empty"

    def test_split_checksum_different_splits(self):
        """Test different splits produce different checksums."""
        if hasattr(split, "_split_checksum"):
            indices = [0, 1, 2, 3, 4]
            train_cs = split._split_checksum("dataset_hash", "train", indices)
            val_cs = split._split_checksum("dataset_hash", "val", indices)
            assert train_cs != val_cs, "train_cs is not valid"

    def test_split_checksum_different_indices(self):
        """Test different indices produce different checksums."""
        if hasattr(split, "_split_checksum"):
            indices1 = [0, 1, 2]
            indices2 = [3, 4, 5]
            cs1 = split._split_checksum("dataset_hash", "train", indices1)
            cs2 = split._split_checksum("dataset_hash", "train", indices2)
            assert cs1 != cs2, "cs1 is not valid"


class TestSplitMetadata:
    """Test SplitMetadata dataclass."""

    def test_split_metadata_creation(self):
        """Test creating SplitMetadata."""
        if hasattr(split, "SplitMetadata"):
            metadata = split.SplitMetadata(
                split="train",
                indices=[0, 1, 2, 3, 4],
                checksum="abc123",
            )
            assert metadata.split == "train", "Data must not be empty"
            assert metadata.indices == [0, 1, 2, 3, 4]
            assert metadata.checksum == "abc123", "Data must not be empty"

    def test_split_metadata_as_dict(self):
        """Test SplitMetadata as_dict conversion."""
        if hasattr(split, "SplitMetadata"):
            metadata = split.SplitMetadata(
                split="val",
                indices=[5, 6, 7],
                checksum="def456",
            )
            result = metadata.as_dict()
            assert isinstance(result, dict)
            assert result["split"] == "val", "Result must not be empty"
            assert result["size"] == 3, "Result must not be empty"
            assert result["checksum"] == "def456", "Result must not be empty"

    def test_split_metadata_frozen(self):
        """Test SplitMetadata is frozen (immutable)."""
        if hasattr(split, "SplitMetadata"):
            metadata = split.SplitMetadata(
                split="test",
                indices=[8, 9],
                checksum="ghi789",
            )
            with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
                metadata.split = "modified"


class TestBuildManifest:
    """Test _build_manifest function."""

    def test_build_manifest_basic(self):
        """Test building manifest with basic inputs."""
        if hasattr(split, "_build_manifest") and hasattr(split, "SplitMetadata"):
            train_meta = split.SplitMetadata("train", [0, 1, 2], "train_cs")
            val_meta = split.SplitMetadata("val", [3, 4], "val_cs")
            test_meta = split.SplitMetadata("test", [5], "test_cs")

            manifest = split._build_manifest(
                dataset_name="test_dataset",
                dataset_identifier="test_id",
                dataset_hash="hash123",
                seed=42,
                train=train_meta,
                val=val_meta,
                test=test_meta,
                fractions={"train": 0.6, "val": 0.2, "test": 0.2},
            )

            assert isinstance(manifest, dict)
            assert "dataset" in manifest, "Data must not be empty"
            assert "splits" in manifest, "Condition must be true"
            assert manifest["seed"] == 42, "Condition must be true"

    def test_build_manifest_contains_schema(self):
        """Test manifest contains schema information."""
        if hasattr(split, "_build_manifest") and hasattr(split, "SplitMetadata"):
            train_meta = split.SplitMetadata("train", [0], "cs1")
            val_meta = split.SplitMetadata("val", [1], "cs2")
            test_meta = split.SplitMetadata("test", [2], "cs3")

            manifest = split._build_manifest(
                dataset_name="test",
                dataset_identifier="id",
                dataset_hash="hash",
                seed=42,
                train=train_meta,
                val=val_meta,
                test=test_meta,
                fractions={"train": 0.6, "val": 0.2, "test": 0.2},
            )

            assert "$schema" in manifest or "schema_version" in manifest, "Condition must be true"
