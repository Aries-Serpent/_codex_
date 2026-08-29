"""
Test Repro Seed Consistency

Test module for repro seed consistency.
"""

import random

import pytest

pytest.importorskip("numpy")

import numpy as np

try:
    import torch
except ImportError:  # pragma: no cover - torch missing
    torch = None  # type: ignore[assignment]

# Prefer top-level re-export if available; fallback to module path
try:
    from codex_ml.utils import set_reproducible  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
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

    assert py1 == py2 and np1 == np2, "py1 is not valid"
    if torch is not None and t1 is not None and t2 is not None:
        # Use tolerance for potential numerical differences in CI
        assert torch.allclose(t1, t2, rtol=1e-5, atol=1e-7), f"Tensors not close: {t1} vs {t2}"
