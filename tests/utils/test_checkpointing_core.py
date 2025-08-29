import json
from pathlib import Path
import random

import pytest

from utils.checkpointing import (
    CheckpointManager,
    dump_rng_state,
    load_rng_state,
    set_seed,
)


def test_rng_roundtrip(monkeypatch):
    set_seed(123)
    state = dump_rng_state()
    py_val = random.random()
    random.random()
    load_rng_state(state)
    assert random.random() == py_val

    np = pytest.importorskip("numpy")
    load_rng_state(state)
    np_val = np.random.rand()
    np.random.rand()
    load_rng_state(state)
    assert np.random.rand() == np_val

    torch = pytest.importorskip("torch")
    load_rng_state(state)
    t_val = torch.rand(1).item()
    torch.rand(1)
    load_rng_state(state)
    assert torch.rand(1).item() == t_val


def test_checkpoint_best_k(tmp_path: Path):
    mgr = CheckpointManager(tmp_path, keep_last=1, keep_best=1)
    mgr.save(1, metrics={"val_loss": 1.0})
    mgr.save(2, metrics={"val_loss": 0.5})
    mgr.save(3, metrics={"val_loss": 0.8})
    # epoch-3 (last) and epoch-2 (best) should remain
    remaining = {p.name for p in tmp_path.glob("epoch-*")}
    assert remaining == {"epoch-2", "epoch-3"}
    best = json.loads((tmp_path / "best.json").read_text())
    assert best["items"][0]["epoch"] == 2
