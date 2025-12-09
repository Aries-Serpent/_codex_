from __future__ import annotations

import pytest

import torch
from src.codex_ml.training.schedulers.registry import get_scheduler_registry


def test_registry_lists_builtins():
    reg = get_scheduler_registry()
    names = reg.list()
    assert "step_lr" in names
    assert "cosine_annealing" in names
    # Descriptions present
    assert isinstance(reg.describe("step_lr"), str)


def test_build_step_lr_and_step_once():
    model = torch.nn.Linear(4, 2)
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    reg = get_scheduler_registry()

    sched = reg.build("step_lr", optimizer=opt, step_size=2, gamma=0.5)
    assert hasattr(sched, "step")
    # Initial LR
    initial_lr = opt.param_groups[0]["lr"]
    # Step scheduler a couple of times; LR should decay at step_size boundaries
    sched.step()  # epoch 1
    assert opt.param_groups[0]["lr"] == pytest.approx(initial_lr)
    sched.step()  # epoch 2 -> decay
    assert opt.param_groups[0]["lr"] == pytest.approx(initial_lr * 0.5)


def test_build_cosine_annealing_progression():
    model = torch.nn.Linear(4, 2)
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    reg = get_scheduler_registry()

    sched = reg.build("cosine_annealing", optimizer=opt, T_max=4, eta_min=0.0)
    lrs = []
    for _ in range(5):
        lrs.append(opt.param_groups[0]["lr"])
        sched.step()
    # LR should vary smoothly between eta_min and initial
    assert max(lrs) <= 0.1 + 1e-9
    assert min(lrs) >= 0.0 - 1e-9
