from __future__ import annotations

from pathlib import Path

import pytest

from codex_ml.utils.checkpoint_manager import load_checkpoint, save_checkpoint


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    target = tmp_path / "checkpoints" / "step-1.pt"
    state = {"epoch": 1, "loss": 0.5}
    save_checkpoint(state, target)
    loaded = load_checkpoint(target)
    assert loaded == state


def test_prunes_old_checkpoints(tmp_path: Path) -> None:
    root = tmp_path / "ckpts"
    for step in range(4):
        save_checkpoint({"step": step}, root / f"ckpt-{step}.pt", keep_last_k=2)
    remaining = sorted(p.name for p in root.glob("*.pt"))
    assert remaining == ["ckpt-2.pt", "ckpt-3.pt"]


def test_load_missing_checkpoint(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_checkpoint(tmp_path / "missing.pt")
