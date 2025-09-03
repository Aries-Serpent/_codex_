import numpy as np
import torch

from codex_ml.utils.repro import set_reproducible


def model():
    return torch.nn.Linear(4, 2, bias=False)


def test_cpu_determinism_small():
    set_reproducible(123)
    m1 = model()
    x = torch.ones(3, 4)
    y1 = m1(x).detach().numpy()
    set_reproducible(123)
    m2 = model()
    y2 = m2(x).detach().numpy()
    assert np.allclose(y1, y2)


def test_set_reproducible_handles_missing(monkeypatch):
    def boom(_):
        raise RuntimeError("fail")

    monkeypatch.setattr(torch, "use_deterministic_algorithms", boom)
    monkeypatch.setattr(torch, "backends", object())
    set_reproducible(1)
