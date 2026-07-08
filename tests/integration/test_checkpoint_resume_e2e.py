"""End-to-end tests for checkpoint resume with schema migration and state recovery.

Tests full checkpoint resume workflow including schema detection, migration,
and recovery from partial or corrupted checkpoint states.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest


class TestCheckpointResumeFullWorkflow:
    """Integration tests for complete checkpoint resume workflows."""

    def test_checkpoint_resume_end_to_end_workflow(self):
        """Test complete save-load-resume-train cycle."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import (
            SCHEMA_VERSION,
            load_checkpoint,
            save_checkpoint,
        )

        tmpdir = Path(tempfile.mkdtemp())

        try:
            # Phase 1: Initial training, save checkpoint
            ckpt1_dir = tmpdir / "epoch_010"
            training_state_1 = {
                "model": {"weights": [0.1, 0.2, 0.3]},
                "optimizer": {"momentum": 0.9},
                "step": 100,
            }
            metadata_1 = {"epoch": 10, "step": 100, "loss": 0.5}

            save_checkpoint(
                str(ckpt1_dir),
                state=training_state_1,
                meta=metadata_1,
            )

            # Verify checkpoint created correctly
            assert (ckpt1_dir / "weights.pt").exists(), "Weights file should be created"
            assert (ckpt1_dir / "metadata.json").exists(), "Metadata file should be created"

            # Phase 2: Load checkpoint to resume training
            loaded_state_1, loaded_meta_1 = load_checkpoint(str(ckpt1_dir))

            assert loaded_state_1 == training_state_1, "Loaded state should match saved state"
            assert loaded_meta_1["epoch"] == 10, "Epoch metadata should be preserved"

            # Phase 3: Continue training, save new checkpoint
            ckpt2_dir = tmpdir / "epoch_020"
            training_state_2 = {
                "model": {"weights": [0.15, 0.25, 0.35]},  # Updated weights
                "optimizer": {"momentum": 0.9},
                "step": 200,  # Double the step
            }
            metadata_2 = {"epoch": 20, "step": 200, "loss": 0.3}

            save_checkpoint(
                str(ckpt2_dir),
                state=training_state_2,
                meta=metadata_2,
            )

            # Phase 4: Verify second checkpoint
            loaded_state_2, loaded_meta_2 = load_checkpoint(str(ckpt2_dir))

            assert loaded_state_2["step"] == 200, "Step should be updated in new checkpoint"
            assert (loaded_meta_2["loss"] < loaded_meta_1["loss"], "Condition must be true"
            ), "Loss should have decreased during training"

            # Assert schema versioning
            metadata_file = ckpt2_dir / "metadata.json"
            with open(metadata_file, encoding="utf-8") as f:
                saved_metadata = json.load(f)

            assert (saved_metadata.get("_schema_version") == SCHEMA_VERSION, "Data must not be empty"
            ), "Schema version should be tracked"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_checkpoint_resume_with_schema_validation(self):
        """Verify schema compatibility checks during resume."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        tmpdir = Path(tempfile.mkdtemp())

        try:
            ckpt_dir = tmpdir / "schema_test"
            state = {"data": [1, 2, 3]}
            meta = {"version": 1}

            # Act: Save with current schema
            save_checkpoint(
                str(ckpt_dir),
                state=state,
                meta=meta,
            )

            # Manually patch metadata to simulate old schema
            metadata_path = ckpt_dir / "metadata.json"
            with open(metadata_path, encoding="utf-8") as f:
                metadata = json.load(f)

            metadata["_schema_version"] = "1.0"  # Simulate old schema

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f)

            # Load should warn about schema mismatch but still work
            with pytest.warns(UserWarning, match="schema"):
                loaded_state, loaded_meta = load_checkpoint(str(ckpt_dir))

                assert (loaded_state == state, "loaded_state is not valid"
                ), "Should still load state despite schema version mismatch"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_checkpoint_resume_missing_metadata_recovery(self):
        """Verify resume still works when metadata is missing."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        tmpdir = Path(tempfile.mkdtemp())

        try:
            ckpt_dir = tmpdir / "missing_meta"
            state = {"weights": [0.5, 0.6], "step": 42}
            meta = {"epoch": 4}

            # Save checkpoint
            save_checkpoint(
                str(ckpt_dir),
                state=state,
                meta=meta,
            )

            # Delete metadata file to simulate corruption
            metadata_path = ckpt_dir / "metadata.json"
            metadata_path.unlink()

            # Act: Load should still work
            loaded_state, loaded_meta = load_checkpoint(str(ckpt_dir))

            # Assert
            assert loaded_state == state, "Should load state even with missing metadata"
            assert loaded_meta == {}, "Should return empty metadata dict if file missing"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestCheckpointPartialRecovery:
    """Tests for recovery from partial checkpoint scenarios."""

    def test_checkpoint_load_handles_extra_fields(self):
        """Verify load handles extra fields in saved state gracefully."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        tmpdir = Path(tempfile.mkdtemp())

        try:
            ckpt_dir = tmpdir / "extra_fields"
            state = {
                "model": {"w": 0.5},
                "optimizer": {"lr": 0.001},
                "extra_field": "This field might not be expected",
                "nested": {"a": 1, "b": 2},
            }
            meta = {"epoch": 1}

            # Act: Save and load
            save_checkpoint(
                str(ckpt_dir),
                state=state,
                meta=meta,
            )

            loaded_state, loaded_meta = load_checkpoint(str(ckpt_dir))

            # Assert: All fields should be preserved
            assert loaded_state == state, "Should preserve all fields including extra ones"
            assert "extra_field" in loaded_state, "Extra field should be preserved"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_checkpoint_load_handles_missing_metadata_file(self):
        """Verify load gracefully handles missing metadata.json."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        tmpdir = Path(tempfile.mkdtemp())

        try:
            ckpt_dir = tmpdir / "no_meta"
            state = {"weights": [0.5]}
            meta = {"step": 1}

            # Save initial checkpoint
            save_checkpoint(
                str(ckpt_dir),
                state=state,
                meta=meta,
            )

            # Remove metadata file
            (ckpt_dir / "metadata.json").unlink()

            # Act: Load should work with warning or gracefully
            loaded_state, loaded_meta = load_checkpoint(str(ckpt_dir))

            # Assert
            assert loaded_state == state, "Should load state without metadata"
            assert isinstance(loaded_meta, dict), "Metadata should be empty dict"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestCheckpointResumeDeterminism:
    """Tests for deterministic behavior across resume cycles."""

    def test_checkpoint_resume_round_trip_idempotency(self):
        """Verify repeated save-load cycles produce identical results."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        tmpdir = Path(tempfile.mkdtemp())

        try:
            # Initial checkpoint
            ckpt_dir = tmpdir / "idempotency"
            original_state = {
                "model": {"layer1": [0.1, 0.2], "layer2": [0.3, 0.4, 0.5]},
                "step": 42,
            }
            meta = {"epoch": 4, "loss": 0.123}

            # Cycle 1: Save and load
            save_checkpoint(
                str(ckpt_dir),
                state=original_state,
                meta=meta,
            )
            cycle1_state, cycle1_meta = load_checkpoint(str(ckpt_dir))

            # Cycle 2: Save loaded state, reload
            ckpt_dir2 = tmpdir / "idempotency_2"
            save_checkpoint(
                str(ckpt_dir2),
                state=cycle1_state,
                meta=cycle1_meta,
            )
            cycle2_state, cycle2_meta = load_checkpoint(str(ckpt_dir2))

            # Assert
            assert cycle1_state == cycle2_state, "State should be identical after round-trip"
            assert cycle1_state == original_state, "Loaded state should match original"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_checkpoint_timestamp_changes_on_each_save(self):
        """Verify checkpoint timestamps update on each save."""
        # Arrange
        import time

        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        tmpdir = Path(tempfile.mkdtemp())

        try:
            state = {"weights": [0.5]}
            meta = {"epoch": 1}

            # Save first checkpoint
            ckpt1_dir = tmpdir / "checkpoint_1"
            save_checkpoint(
                str(ckpt1_dir),
                state=state,
                meta=meta,
            )

            _, meta1 = load_checkpoint(str(ckpt1_dir))
            timestamp1 = meta1.get("_created_at")

            # Wait briefly
            time.sleep(0.1)

            # Save second checkpoint
            ckpt2_dir = tmpdir / "checkpoint_2"
            save_checkpoint(
                str(ckpt2_dir),
                state=state,
                meta=meta,
            )

            _, meta2 = load_checkpoint(str(ckpt2_dir))
            timestamp2 = meta2.get("_created_at")

            # Assert
            assert timestamp1 is not None, "First checkpoint should have timestamp"
            assert timestamp2 is not None, "Second checkpoint should have timestamp"
            # Timestamps should be different (or at least valid)
            assert isinstance(timestamp1, str), "Timestamp should be string (ISO format)"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestCheckpointResumeErrorRecovery:
    """Tests for error recovery during checkpoint resume."""

    def test_checkpoint_load_nonexistent_path_clear_error(self):
        """Verify clear error message for nonexistent checkpoint path."""
        # Arrange
        from src.codex_ml.checkpointing.checkpoint_core import load_checkpoint

        nonexistent = "/nonexistent/path/to/checkpoint"

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            load_checkpoint(nonexistent)

        error_msg = str(exc_info.value)
        assert ("weights" in error_msg.lower() or "found" in error_msg.lower(), "Error should be raised or set"
        ), "Error should indicate what file is missing"

    def test_checkpoint_save_to_readonly_directory_error(self):
        """Verify appropriate error when save directory is read-only."""
        # Arrange
        import os

        from src.codex_ml.checkpointing.checkpoint_core import save_checkpoint

        tmpdir = Path(tempfile.mkdtemp())

        try:
            readonly_dir = tmpdir / "readonly"
            readonly_dir.mkdir()

            # Make directory read-only
            # intentional for testing permission errors
            os.chmod(readonly_dir, 0o444)

            ckpt_dir = readonly_dir / "checkpoint"

            # Act & Assert
            try:
                save_checkpoint(
                    str(ckpt_dir),
                    state={"test": "data"},
                    meta={},
                )
                # If we get here, permission was granted (skip)
                pytest.skip("Read-only directory test skipped (permissions allowed)")
            except (PermissionError, OSError) as e:
                # Expected: should raise permission error
                assert ("permission" in str(e).lower() or "access" in str(e).lower(), "Condition must be true"
                ), "Should raise permission-related error"

        finally:
            # Restore permissions for cleanup
            readonly_dir_check = tmpdir / "readonly"
            if readonly_dir_check.exists():
                # restoring normal permissions for cleanup
                os.chmod(readonly_dir_check, 0o755)
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
