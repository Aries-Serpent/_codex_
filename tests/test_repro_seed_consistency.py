import random

import numpy as np

try:
    import torch
except Exception:  # pragma: no cover - torch missing
    torch = None  # type: ignore[assignment]

# Prefer top-level re-export if available; fallback to module path
try:
    from codex_ml.utils import set_reproducible  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    from codex_ml.utils.repro import set_reproducible  # type: ignore


def test_set_reproducible_repeatable():
    seed = 42
    set_reproducible(seed)
    py1 = random.random()
    np1 = np.random.rand()
    t1 = torch.rand(1) if torch is not None else None

    set_reproducible(seed)
    py2 = random.random()
    np2 = np.random.rand()
    t2 = torch.rand(1) if torch is not None else None

    assert py1 == py2 and np1 == np2
    if torch is not None:
        assert torch.allclose(t1, t2)  # type: ignore[arg-type]
