"""
Test Checkpoint Load Roundtrip

Test module for checkpoint load roundtrip.
"""

from pathlib import Path

from codex_ml.utils import checkpoint_core
from codex_ml.utils.checkpoint_core import load_checkpoint, save_checkpoint


def test_load_roundtrip(tmp_path: Path):
    out = tmp_path / "epoch-0"
    save_checkpoint(out, payload={"model_state": {"w": 1}}, metadata={"epoch": 0})
    state, meta = load_checkpoint(out)
    assert "model_state" in state, "Condition must be true"
    assert state["model_state"]["w"] == 1, "Condition must be true"
    assert meta.schema_version == checkpoint_core.SCHEMA_VERSION, "schema_version is not valid"
