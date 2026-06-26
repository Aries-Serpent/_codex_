"""
Test Checkpoint Utils

Test module for checkpoint utils.
"""

from pathlib import Path

from codex_ml.checkpointing import utils


def test_save_and_load_roundtrip(tmp_path: Path):
    cp = tmp_path / "cp.json"
    payload = {"value": 123}
    utils.save_checkpoint(cp, payload)
    loaded = utils.load_checkpoint(cp)
    assert loaded == payload, "loaded is not valid"
