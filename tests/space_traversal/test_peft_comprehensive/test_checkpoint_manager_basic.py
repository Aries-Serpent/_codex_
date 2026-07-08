"""
Test Checkpoint Manager Basic

Verifies step-based checkpoint saving and keep_last pruning behavior.
"""

import json
from types import SimpleNamespace

import pytest

# numpy is pulled in transitively by training/__init__.py → functional_training.py;
# skip at collection time rather than crashing with an ImportError.
pytest.importorskip("numpy")

from training.checkpoint_manager import CheckpointManager  # noqa: E402

pytestmark = pytest.mark.requires_torch

torch = pytest.importorskip("torch")


def test_manager_basic(tmp_path):
    model = torch.nn.Linear(2, 2)
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda _: 1.0)

    mgr = CheckpointManager(tmp_path, save_steps=2, keep_last=1)
    cb = mgr.callback()
    state = SimpleNamespace(global_step=0, epoch=0)
    control = SimpleNamespace()

    cb.on_train_begin(None, state, control, model=model, optimizer=opt, lr_scheduler=sched)
    for step in range(1, 5):
        state.global_step = step
        cb.on_step_end(None, state, control)

    ckpts = list(tmp_path.glob("step-*.pt"))
    assert len(ckpts) == 1, "Ckpts must not be empty"
    assert ckpts[0].name == "step-4.pt", "name is not valid"


def test_maybe_save_ignores_zero_save_steps(tmp_path):
    mgr = CheckpointManager(tmp_path, keep_last=2)
    assert mgr.maybe_save(step=0, payload=b"x", metrics=None, save_steps=0) is None
    assert list(tmp_path.glob("ckpt-*.pt")) == [], "Condition must be true"


def test_prune_preserves_best_checkpoint_when_best_path_is_absolute(tmp_path):
    best_path = tmp_path / "ckpt-1.pt"
    (tmp_path / "best.json").write_text(
        json.dumps({"items": [{"path": str(best_path), "value": 0.1, "step": 1}]}),
        encoding="utf-8",
    )
    mgr = CheckpointManager(tmp_path, keep_last=1, metric="loss", keep_best=1)
    mgr.save_now(1, b"a", {"loss": 0.1})
    mgr.save_now(2, b"b", {"loss": 0.2})
    assert (tmp_path / "ckpt-1.pt").exists(), "Condition must be true"
    assert (tmp_path / "ckpt-2.pt").exists(), "Condition must be true"
