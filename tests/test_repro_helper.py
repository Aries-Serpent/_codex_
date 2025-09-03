import random

import numpy as np

try:
    import torch
except Exception:  # pragma: no cover - torch missing
    torch = None

from codex_ml.utils import set_reproducible


def test_set_reproducible_cpu():
    set_reproducible(123)
    a1 = random.random()
    n1 = np.random.rand()
    t1 = torch.rand(1) if torch is not None else None

    set_reproducible(123)
    a2 = random.random()
    n2 = np.random.rand()
    t2 = torch.rand(1) if torch is not None else None

    assert a1 == a2 and n1 == n2
    if torch is not None:
        assert torch.allclose(t1, t2)
