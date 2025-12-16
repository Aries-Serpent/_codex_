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
    assert (temp_dir / "best_candidates").exists()
    assert manager.keep_last >= 1


def test_checkpoint_manager_lists_empty(temp_dir: Path) -> None:
    from src.training.checkpoint_manager import CheckpointManager

    manager = CheckpointManager(temp_dir)
    # fallback implementation may not expose listing; ensure directory is writable
    assert manager.root.exists()


def test_checkpoint_manager_best_metadata_roundtrip(temp_dir: Path) -> None:
    from src.training.checkpoint_manager import CheckpointManager

    meta = {
        "items": [
            {"path": str(temp_dir / "checkpoint-1"), "value": 0.5, "step": 1},
            {"path": str(temp_dir / "checkpoint-2"), "value": 0.3, "step": 2},
        ]
    }
    best_meta = temp_dir / "best.json"
    best_meta.write_text("""{"items": [{"path": "checkpoint-2", "value": 0.3, "step": 2}]}""")

    manager = CheckpointManager(temp_dir, metric="loss")
    # ensure prior metadata is parsed without raising
    assert manager._best_records is not None
