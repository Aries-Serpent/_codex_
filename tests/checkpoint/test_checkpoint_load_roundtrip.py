from codex_ml.utils.checkpoint_core import save_checkpoint, load_checkpoint
from pathlib import Path


def test_load_roundtrip(tmp_path: Path):
    out = tmp_path / "epoch-0"
    save_checkpoint(out, payload={"model_state": {"w": 1}}, metadata={"epoch": 0})
    state = load_checkpoint(out)
    assert "model_state" in state
    assert state["model_state"]["w"] == 1
