"""
Test Checkpoint Manager Callback

Test module for checkpoint manager callback.
"""

from __future__ import annotations

import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")

from torch.optim import SGD

import torch
from training.checkpoint_manager import CheckpointManager
from transformers import TrainerControl, TrainerState


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


def test_callback_can_save_at_step_zero(tmp_path):
    model = torch.nn.Linear(1, 1)
    opt = SGD(model.parameters(), lr=0.1)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda _: 1.0)
    mgr = CheckpointManager(tmp_path, save_steps=1, keep_last=2)
    cb = mgr.callback()
    state = TrainerState()
    control = TrainerControl()
    cb.on_train_begin(None, state, control, model=model, optimizer=opt, lr_scheduler=sched)
    state.global_step = 0
    state.epoch = 0
    cb.on_step_end(None, state, control)
    checkpoint_path = tmp_path / "step-0.pt"
    assert checkpoint_path.exists(), "Condition must be true"
    payload = torch.load(checkpoint_path, map_location="cpu")
    assert "model" in payload, "Condition must be true"
    assert "optimizer" in payload, "Condition must be true"
