import random

import numpy as np

try:
    import torch
except Exception:  # pragma: no cover - torch missing
    torch = None

from codex_ml.utils import set_reproducible


def test_set_reproducible_repeatable():
    set_reproducible(42)
    py1 = random.random()
    np1 = np.random.rand()
    t1 = torch.rand(1) if torch is not None else None

    set_reproducible(42)
    py2 = random.random()
    np2 = np.random.rand()
    t2 = torch.rand(1) if torch is not None else None

    assert py1 == py2 and np1 == np2
    if torch is not None:
        assert torch.allclose(t1, t2)
