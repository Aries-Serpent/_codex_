"""
Test Checkpoint Core Io

Test module for checkpoint core io.
"""

from __future__ import annotations

from codex_ml.utils import checkpoint_core


def test_save_and_load_roundtrip(tmp_path) -> None:
    ckpt_dir = tmp_path / "epoch-0"
    payload = {
        "model_state": {"w": [1, 2]},
        "optimizer_state": {"beta": 0.9},
    }
    metadata = {"metrics": {"loss": 0.25}}
    state_path, _meta = checkpoint_core.save_checkpoint(
        ckpt_dir,
        payload=payload,
        metadata=metadata,
        include_rng=False,
    )
    assert state_path.exists()

    loaded_state, loaded_meta = checkpoint_core.load_checkpoint(ckpt_dir)
    assert loaded_state["model_state"] == payload["model_state"]
    assert loaded_state["optimizer_state"] == payload["optimizer_state"]
    assert loaded_meta.schema_version == checkpoint_core.SCHEMA_VERSION
    assert loaded_meta.rng == {}  # include_rng was False
