from __future__ import annotations

import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")

import torch
from torch.optim import SGD
from transformers import TrainerControl, TrainerState

from training.checkpoint_manager import CheckpointManager


def test_callback_saves_and_prunes(tmp_path):
    model = torch.nn.Linear(1, 1)
    opt = SGD(model.parameters(), lr=0.1)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda _: 1.0)
    mgr = CheckpointManager(tmp_path, save_steps=1, keep_last=2)
    cb = mgr.callback()
    state = TrainerState()
    control = TrainerControl()
    cb.on_train_begin(None, state, control, model=model, optimizer=opt, lr_scheduler=sched)

    for step in range(3):
        state.global_step = step + 1
        state.epoch = step + 1
        cb.on_step_end(None, state, control)

    ckpts = sorted(p.name for p in tmp_path.glob("step-*.pt"))
    assert ckpts == ["step-2.pt", "step-3.pt"]
