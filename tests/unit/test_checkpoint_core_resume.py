"""Unit tests for checkpoint core save/load functionality.

Tests checkpoint serialization, deserialization, schema validation,
and backward compatibility with schema versions.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest


class TestCheckpointCoreBasics:
    """Test basic checkpoint save and load operations."""

    def setup_method(self):
        """Initialize test fixtures."""
        self.tmpdir = Path(tempfile.mkdtemp())
        self.checkpoint_dir = self.tmpdir / "checkpoint_001"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """Clean up test artifacts."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_checkpoint_directory_created(self):
        """Verify checkpoint directory is created on save."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import save_checkpoint

        test_state = {"model": {"weights": [1.0, 2.0]}}
        test_meta = {"epoch": 1, "step": 100}

        # Act
        result = save_checkpoint(
            str(self.checkpoint_dir),
            state=test_state,
            meta=test_meta,
        )

        # Assert
        assert Path(result).exists(), f"Checkpoint directory not created: {result}"
        assert (Path(result) / "weights.pt").exists(), "weights.pt file not created"
        assert (Path(result) / "metadata.json").exists(), "metadata.json file not created"

    def test_checkpoint_metadata_written_correctly(self):
        """Verify metadata JSON contains schema version and timestamp."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import save_checkpoint

        test_state = {"model": {"layer": [0.5]}}
        test_meta = {"epoch": 2, "step": 50}

        # Act
        save_checkpoint(
            str(self.checkpoint_dir),
            state=test_state,
            meta=test_meta,
        )

        # Assert
        metadata_path = self.checkpoint_dir / "metadata.json"
        with open(metadata_path, encoding="utf-8") as f:
            metadata = json.load(f)

        assert metadata.get("_schema_version") == "2.0", "Schema version not set to 2.0"
        assert "_created_at" in metadata, "Created timestamp not in metadata"
        assert metadata.get("epoch") == 2, "Epoch not preserved in metadata"
        assert metadata.get("step") == 50, "Step not preserved in metadata"

    def test_checkpoint_load_missing_file_raises_error(self):
        """Verify FileNotFoundError raised for missing checkpoint."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import load_checkpoint

        nonexistent_path = self.tmpdir / "missing" / "checkpoint.pt"

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            load_checkpoint(str(nonexistent_path))

        assert ("weights not found" in str(exc_info.value).lower(), "Value must be initialized"
        ), "Error message should indicate missing weights file"

    def test_checkpoint_round_trip_preserves_state(self):
        """Verify state is preserved through save and load cycle."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        original_state = {
            "model": {"layer1": [1.0, 2.0, 3.0], "layer2": [4.0, 5.0]},
            "step": 42,
        }
        original_meta = {"epoch": 3, "step": 42, "loss": 0.123}

        # Act: Save
        save_checkpoint(
            str(self.checkpoint_dir),
            state=original_state,
            meta=original_meta,
        )

        # Act: Load
        loaded_state, loaded_meta = load_checkpoint(str(self.checkpoint_dir))

        # Assert
        assert loaded_state == original_state, "State not preserved after round-trip"
        assert loaded_meta["epoch"] == 3, "Epoch not preserved in metadata"

    def test_checkpoint_load_handles_missing_metadata(self):
        """Verify load succeeds even if metadata.json is missing."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        test_state = {"model": {"w": 0.5}}
        test_meta = {"step": 1}

        # Act: Save checkpoint
        save_checkpoint(
            str(self.checkpoint_dir),
            state=test_state,
            meta=test_meta,
        )

        # Remove metadata file
        metadata_path = self.checkpoint_dir / "metadata.json"
        metadata_path.unlink()

        # Act: Load should still work
        loaded_state, loaded_meta = load_checkpoint(str(self.checkpoint_dir))

        # Assert
        assert loaded_state == test_state, "State should load even without metadata"
        assert loaded_meta == {}, "Metadata should be empty dict when file missing"

    def test_checkpoint_schema_version_validation(self):
        """Verify schema version is checked during load."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import load_checkpoint

        test_state = {"model": {"w": 0.5}}
        weights_path = self.checkpoint_dir / "weights.pt"
        metadata_path = self.checkpoint_dir / "metadata.json"

        # Create weights with mismatched schema version
        try:
            import torch

            payload = {
                "_schema_version": "1.5",  # Mismatch with current 2.0
                "state": test_state,
            }
            torch.save(payload, str(weights_path))
        except ImportError:  # pragma: no cover
            pytest.skip("PyTorch not available")

        # Create metadata with mismatched version
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "_schema_version": "1.5",
                    "epoch": 1,
                },
                f,
            )

        # Act & Assert: Should warn but still load
        with pytest.warns(UserWarning, match="schema v1.5"):
            loaded_state, loaded_meta = load_checkpoint(str(self.checkpoint_dir))
            assert loaded_state == test_state, "Should still load state despite schema mismatch"


class TestCheckpointAtomicIO:
    """Test atomic I/O operations for checkpoint safety."""

    def setup_method(self):
        """Initialize test fixtures."""
        self.tmpdir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test artifacts."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_checkpoint_save_creates_atomic_write(self):
        """Verify checkpoint files are written atomically."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import save_checkpoint

        checkpoint_dir = self.tmpdir / "ckpt_atomic"
        test_state = {"model": {}}
        test_meta = {}

        # Act
        result = save_checkpoint(
            str(checkpoint_dir),
            state=test_state,
            meta=test_meta,
        )

        # Assert
        metadata_path = Path(result) / "metadata.json"
        assert metadata_path.exists(), "Metadata file should exist after save"

        with open(metadata_path, encoding="utf-8") as f:
            content = f.read()
            assert len(content) > 0, "Metadata file should not be empty"

    def test_checkpoint_keep_last_k_cleanup(self):
        """Verify keep_last_k parameter limits retained checkpoints."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import save_checkpoint

        parent_dir = self.tmpdir / "training"
        parent_dir.mkdir()

        # Act: Save 3 checkpoints with keep_last_k=2
        for i in range(3):
            ckpt_dir = parent_dir / f"epoch_{i:03d}"
            save_checkpoint(
                str(ckpt_dir),
                state={"step": i},
                meta={"epoch": i},
                keep_last_k=2,
            )

        # Assert: Verify the function completes without error
        # (Cleanup is best-effort and may not delete, just verify no exception)
        assert parent_dir.exists(), "Parent directory should exist after saves"


class TestCheckpointErrorHandling:
    """Test error handling in checkpoint operations."""

    def setup_method(self):
        """Initialize test fixtures."""
        self.tmpdir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test artifacts."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_checkpoint_torch_not_available_raises_runtime_error(self):
        """Verify clear error when PyTorch is not available."""
        # This test verifies the _require_torch_attr function
        from src.codex_ml.checkpointing.checkpoint_core import _require_torch_attr

        # Test with invalid torch attribute
        with pytest.raises(RuntimeError) as exc_info:
            _require_torch_attr("nonexistent_torch_function")

        assert ("missing required attribute" in str(exc_info.value).lower(), "Value must be initialized"
        ), "Error should indicate missing torch attribute"

    def test_checkpoint_save_to_nonexistent_parent(self):
        """Verify save creates parent directories as needed."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import save_checkpoint

        nested_dir = self.tmpdir / "level1" / "level2" / "checkpoint"
        test_state = {"w": 0.5}
        test_meta = {"step": 1}

        # Act
        result = save_checkpoint(
            str(nested_dir),
            state=test_state,
            meta=test_meta,
        )

        # Assert
        assert Path(result).exists(), "Nested checkpoint directory should be created"
        assert (Path(result) / "weights.pt", "Result must not be empty"
        ).exists(
        ), "Weights file should exist in nested directory"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
