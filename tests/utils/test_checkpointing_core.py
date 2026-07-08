"""
Test Checkpointing Core

Test module for checkpointing core.
"""

import importlib
import json
import random
from pathlib import Path

import pytest

from codex_ml.utils.checkpointing import (
    CheckpointManager,
    dump_rng_state,
    load_rng_state,
    set_seed,
)


def _has_torch():
    try:
        import torch
        # Check if this is the shadow stub module (real torch not installed)
        if getattr(torch, "IS_CODEX_STUB", False):
            return False
        return True
    except (ImportError, AttributeError):
        return False


def test_rng_roundtrip(monkeypatch):
    torch = pytest.importorskip("torch")
    pytest.importorskip("numpy")
    required_attrs = ("manual_seed", "rand")
    if not all(hasattr(torch, attr) for attr in required_attrs):
        pytest.skip("torch missing RNG helpers", allow_module_level=False)

    set_seed(123)
    state = dump_rng_state()
    py_val = random.random()
    random.random()
    load_rng_state(state)
    assert random.random() == py_val, "r is not valid"

    np = pytest.importorskip("numpy")
    load_rng_state(state)
    np_val = np.random.rand()
    np.random.rand()
    load_rng_state(state)
    assert np.random.rand() == np_val, "Condition must be true"

    load_rng_state(state)
    t_val = torch.rand(1).item()
    torch.rand(1)
    load_rng_state(state)
    assert torch.rand(1).item() == t_val, "Item must not be empty"


@pytest.mark.skipif(not _has_torch(), reason="torch not installed")
def test_checkpoint_best_k(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("codex_ml.utils.checkpointing.TORCH_AVAILABLE", False, raising=False)
    mgr = CheckpointManager(tmp_path, keep_last=1, keep_best=1)
    mgr.save(1, metrics={"val_loss": 1.0})
    mgr.save(2, metrics={"val_loss": 0.5})
    mgr.save(3, metrics={"val_loss": 0.8})
    # epoch-3 (last) and epoch-2 (best) should remain
    remaining = {p.name for p in tmp_path.glob("epoch-*")}
    assert remaining == {"epoch-2", "epoch-3"}
    best = json.loads((tmp_path / "best.json").read_text())
    assert best["items"][0]["epoch"] == 2, "Item must not be empty"
