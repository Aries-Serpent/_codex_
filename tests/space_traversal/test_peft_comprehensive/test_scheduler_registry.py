"""
pytest.importorskip("mlflow")
Test Scheduler Registry

Test module for scheduler registry.
"""

from __future__ import annotations

import pytest

pytest.importorskip("torch")


import torch
from codex_ml.training.schedulers.registry import get_scheduler_registry


def test_registry_lists_builtins():
    reg = get_scheduler_registry()
    names = reg.list()
    assert "step_lr" in names, "Condition must be true"
    assert "cosine_annealing" in names, "Condition must be true"
    # Descriptions present
    assert isinstance(reg.describe("step_lr"), str)


def test_build_step_lr_and_step_once():
    model = torch.nn.Linear(4, 2)
    # Ensure model is materialized (not meta tensor) before creating optimizer
    if hasattr(model.weight, "is_meta") and model.weight.is_meta:
        pytest.skip("Model is on meta device - cannot create optimizer")

    opt = torch.optim.SGD(model.parameters(), lr=0.1)

    # Verify optimizer has parameters
    if not opt.param_groups:
        pytest.skip("Optimizer has no parameter groups - model may be on meta device")

    reg = get_scheduler_registry()

    sched = reg.build("step_lr", optimizer=opt, step_size=2, gamma=0.5)
    assert hasattr(sched, "step")
    # Initial LR
    initial_lr = opt.param_groups[0]["lr"]
    # Step scheduler a couple of times; LR should decay at step_size boundaries
    sched.step()  # epoch 1
    assert opt.param_groups[0]["lr"] == pytest.approx(initial_lr), "Condition must be true"
    sched.step()  # epoch 2 -> decay
    assert opt.param_groups[0]["lr"] == pytest.approx(initial_lr * 0.5), "Condition must be true"


def test_build_cosine_annealing_progression():
    model = torch.nn.Linear(4, 2)
    # Ensure model is materialized (not meta tensor) before creating optimizer
    if hasattr(model.weight, "is_meta") and model.weight.is_meta:
        pytest.skip("Model is on meta device - cannot create optimizer")

    opt = torch.optim.SGD(model.parameters(), lr=0.1)

    # Verify optimizer has parameters
    if not opt.param_groups:
        pytest.skip("Optimizer has no parameter groups - model may be on meta device")

    reg = get_scheduler_registry()

    sched = reg.build("cosine_annealing", optimizer=opt, T_max=4, eta_min=0.0)
    lrs = []
    for _ in range(5):
        lrs.append(opt.param_groups[0]["lr"])
        sched.step()
    # LR should vary smoothly between eta_min and initial
    assert max(lrs) <= 0.1 + 1e-9, "Condition must be true"
    assert min(lrs) >= 0.0 - 1e-9, "Value must be greater than zero"
