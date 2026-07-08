"""Tests for remote checkpoint synchronisation helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

pytest.importorskip("fsspec")

from codex_ml.utils.checkpointing import CheckpointManager
from codex_ml.utils.storage import FSSpecStorage


class _DummyModule:
    def state_dict(self) -> dict[str, int]:
        return {"value": 1}

    def load_state_dict(
        self, state_dict, strict: bool = True
    ) -> None:  # pragma: no cover - smoke path
        assert state_dict["value"] == 1, "Value must be initialized"


def test_checkpoint_manager_remote_roundtrip(tmp_path: Path) -> None:
    storage = FSSpecStorage("memory://codex-checkpoints")
    local_root = tmp_path / "checkpoints"
    manager = CheckpointManager(
        local_root,
        storage=storage,
        remote_prefix="runs/demo",
    )

    manager.save(1, model=_DummyModule(), metrics={"loss": 0.1})

    # Remove local checkpoints to force remote download during resume.
    shutil.rmtree(local_root)

    fresh_manager = CheckpointManager(
        local_root,
        storage=storage,
        remote_prefix="runs/demo",
    )

    info = fresh_manager.load_latest()
    assert info["path"].exists(), "Condition must be true"
    assert (info["path"] / "meta.json").exists(), "Condition must be true"
