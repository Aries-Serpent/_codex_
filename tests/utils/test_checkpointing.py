from __future__ import annotations

import importlib

import pytest


def test_set_seed(tmp_path):
    mod = importlib.import_module("codex_ml.utils.checkpointing")
    seeds = mod.set_seed(42, tmp_path)
    assert seeds["python"] == 42
    assert (tmp_path / "seeds.json").exists()


def test_load_checkpoint_corrupt(tmp_path):
    mod = importlib.import_module("codex_ml.utils.checkpointing")
    bad = tmp_path / "bad.pt"
    bad.write_bytes(b"garbage")

    class M:
        def load_state_dict(self, *a, **k):
            pass

    with pytest.raises(mod.CheckpointLoadError):
        mod.load_training_checkpoint(str(bad), M())
