"""Comprehensive tests for checkpoint integrity verification and checksum validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

pytest.importorskip("torch")

import torch

from codex_ml.utils.checkpointing import (
    CheckpointManager,
    load_training_checkpoint,
    save_checkpoint,
    save_ckpt,
    verify_ckpt_integrity,
)


class MockModel:
    """Mock model for testing checkpoint functionality."""

    def __init__(self, weights: Dict[str, Any] | None = None):
        self.weights = weights or {"layer.weight": torch.tensor([1.0, 2.0, 3.0])}

    def state_dict(self):
        return self.weights.copy()

    def load_state_dict(self, state_dict):
        self.weights.update(state_dict)


class MockOptimizer:
    """Mock optimizer for testing checkpoint functionality."""

    def __init__(self):
        self.state = {"lr": 0.001, "momentum": 0.9}

    def state_dict(self):
        return self.state.copy()

    def load_state_dict(self, state_dict):
        self.state.update(state_dict)


@pytest.fixture
def mock_model():
    """Fixture providing a mock model."""
    return MockModel()


@pytest.fixture
def mock_optimizer():
    """Fixture providing a mock optimizer."""
    return MockOptimizer()


def test_checkpoint_checksum_verify(tmp_path: Path):
    """Test checkpoint checksum verification through CheckpointManager."""
    cm = CheckpointManager(tmp_path)

    # Save a checkpoint
    ckpt_dir = cm.save(1, model=None)

    # Verify checksum file was created
    checksums_file = ckpt_dir / "checksums.json"
    assert checksums_file.exists()

    # Read and verify checksum metadata
    meta = json.loads(checksums_file.read_text())
    assert "file" in meta
    assert "sha256" in meta
    assert "bytes" in meta
    assert len(meta["sha256"]) == 64  # SHA256 hex length

    # Verify that resume works with valid checksum
    cm.resume_from(ckpt_dir)

    # Corrupt the state file and verify that resume fails
    state_file = ckpt_dir / meta["file"]
    original_content = state_file.read_bytes()
    state_file.write_bytes(b"corrupt_data")

    with pytest.raises(RuntimeError, match="checksum mismatch"):
        cm.resume_from(ckpt_dir)

    # Restore original content for cleanup
    state_file.write_bytes(original_content)


def test_checksum_roundtrip(tmp_path):
    """Test checksum creation and verification with save_ckpt and verify_ckpt_integrity."""
    ckpt_path = tmp_path / "model.pt"
    test_state = {"weights": torch.tensor([1.0, 2.0, 3.0])}

    # Save checkpoint with checksum
    save_ckpt(test_state, str(ckpt_path))

    # Verify checkpoint file exists
    assert ckpt_path.exists()

    # Verify checksum metadata file was created
    checksums_file = tmp_path / "checksums.json"
    assert checksums_file.exists()

    # Verify checksum metadata content
    meta = json.loads(checksums_file.read_text())
    assert meta["file"] == "model.pt"
    assert len(meta["sha256"]) == 64
    assert meta["bytes"] == ckpt_path.stat().st_size

    # Verify integrity check passes
    verify_ckpt_integrity(str(ckpt_path))

    # Test with corrupted file
    original_content = ckpt_path.read_bytes()
    ckpt_path.write_bytes(b"corrupted")

    with pytest.raises(RuntimeError, match="checksum mismatch"):
        verify_ckpt_integrity(str(ckpt_path))

    # Restore for cleanup
    ckpt_path.write_bytes(original_content)


def test_checksum_missing_file(tmp_path):
    """Test behavior when checksum file is missing."""
    ckpt_path = tmp_path / "model.pt"
    test_state = {"weights": torch.tensor([1.0])}

    # Save checkpoint without checksum (directly with torch.save)
    torch.save(test_state, ckpt_path)

    # Verify integrity check passes when no checksum file exists
    verify_ckpt_integrity(str(ckpt_path))  # Should not raise


def test_checksum_file_mismatch(tmp_path):
    """Test behavior when checksum file references wrong file."""
    ckpt_path = tmp_path / "model.pt"
    test_state = {"weights": torch.tensor([1.0])}

    # Save checkpoint
    save_ckpt(test_state, str(ckpt_path))

    # Modify checksum file to reference different file
    checksums_file = tmp_path / "checksums.json"
    meta = json.loads(checksums_file.read_text())
    meta["file"] = "different_file.pt"
    checksums_file.write_text(json.dumps(meta))

    # Verify integrity check passes (wrong file name is ignored)
    verify_ckpt_integrity(str(ckpt_path))


def test_save_load_checkpoint_with_integrity(tmp_path, mock_model, mock_optimizer):
    """Test high-level save/load functions with integrity verification."""
    ckpt_path = tmp_path / "checkpoint.pt"

    # Save checkpoint using high-level function
    save_checkpoint(
        str(ckpt_path),
        mock_model,
        mock_optimizer,
        scheduler=None,
        epoch=5,
        extra={"validation_loss": 0.25},
    )

    # Verify checkpoint and checksum files exist
    assert ckpt_path.exists()
    assert (tmp_path / "checksums.json").exists()

    # Create new model/optimizer instances
    new_model = MockModel({"layer.weight": torch.zeros(3)})
    new_optimizer = MockOptimizer()
    new_optimizer.state = {"lr": 0.01}  # Different initial state

    # Load checkpoint
    epoch, extra = load_training_checkpoint(str(ckpt_path), new_model, new_optimizer)

    # Verify loaded data
    assert epoch == 5
    assert extra["validation_loss"] == 0.25
    assert torch.allclose(new_model.weights["layer.weight"], torch.tensor([1.0, 2.0, 3.0]))


def test_load_checkpoint_checksum_mismatch(tmp_path):
    """Corrupt checkpoint file and ensure load_checkpoint detects mismatch."""
    model = MockModel()
    optimizer = MockOptimizer()
    ckpt_path = tmp_path / "ckpt.pt"
    save_checkpoint(str(ckpt_path), model, optimizer, None, epoch=1, extra={})
    # Corrupt checkpoint file after saving
    ckpt_path.write_bytes(b"corrupted")
    new_model = MockModel()
    new_optimizer = MockOptimizer()
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        load_training_checkpoint(str(ckpt_path), new_model, new_optimizer)
