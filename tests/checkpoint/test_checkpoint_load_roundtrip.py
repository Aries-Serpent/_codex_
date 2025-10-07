from __future__ import annotations

from pathlib import Path

from codex_ml.utils.checkpoint_core import load_checkpoint, save_checkpoint


def test_load_roundtrip(tmp_path: Path):
    out = tmp_path / "epoch-0"
    save_checkpoint(out, payload={"model_state": {"w": 1}}, metadata={"epoch": 0})
    state = load_checkpoint(out)
    assert "model_state" in state
    assert state["model_state"]["w"] == 1
