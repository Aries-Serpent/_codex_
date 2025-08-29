import json
import random
from pathlib import Path

from codex_ml.utils.checkpointing import CheckpointManager, dump_rng_state, load_rng_state


def test_dump_load_rng_state():
    random.seed(123)
    state = dump_rng_state()
    a = random.random()
    random.seed(456)
    load_rng_state(state)
    b = random.random()
    assert a == b


def test_checkpoint_manager_best_k(tmp_path: Path):
    mgr = CheckpointManager(tmp_path, keep_last=1, keep_best=2)
    for i, loss in enumerate([5, 3, 4, 2, 1], start=1):
        mgr.save(i, metrics={"val_loss": loss})
    best = json.loads((tmp_path / "best.json").read_text())["items"]
    assert len(best) == 2
    losses = [item["metrics"]["val_loss"] for item in best]
    assert losses == sorted(losses)
