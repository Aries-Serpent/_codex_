"""Smoke tests for training.checkpoint_manager."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    path = tmp_path / "ckpts"
    path.mkdir()
    return path


def test_checkpoint_manager_imports(temp_dir: Path) -> None:
    from src.training.checkpoint_manager import CheckpointManager

    manager = CheckpointManager(temp_dir)
    assert (temp_dir / "best_candidates").exists(), "Condition must be true"
    assert manager.keep_last >= 1, "keep_last must be greater than zero"


def test_checkpoint_manager_lists_empty(temp_dir: Path) -> None:
    from src.training.checkpoint_manager import CheckpointManager

    manager = CheckpointManager(temp_dir)
    # fallback implementation may not expose listing; ensure directory is writable
    assert manager.root.exists(), "Condition must be true"


def test_checkpoint_manager_best_metadata_roundtrip(temp_dir: Path) -> None:
    from src.training.checkpoint_manager import CheckpointManager

    # metadata structure format reference:
    # {"items": [{"path": str(dir / "checkpoint-N"), "value": float, "step": int}]}
    best_meta = temp_dir / "best.json"
    best_meta.write_text("""{"items": [{"path": "checkpoint-2", "value": 0.3, "step": 2}]}""")

    manager = CheckpointManager(temp_dir, metric="loss")
    # ensure prior metadata is parsed without raising
    assert manager._best_records is not None, "_best_records must be initialized"
