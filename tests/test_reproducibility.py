"""
Test Reproducibility

Test module for reproducibility.
"""

import random

import pytest

pytest.importorskip("numpy")
pytest.importorskip("torch")

import numpy as np

from codex_ml.utils.repro import set_reproducible


def test_set_reproducible_reseeds_all():
    # Ensure real torch is imported before calling set_reproducible
    # Patch the seeding module to use real torch
    import sys

    import torch as real_torch

    # Temporarily replace torch in sys.modules to ensure seeding uses real torch
    original_torch = sys.modules.get("torch")
    sys.modules["torch"] = real_torch

    try:
        set_reproducible(123)
        r_py = random.random()
        r_np = np.random.rand()
        r_torch = real_torch.rand(1).item()

        set_reproducible(123)
        assert random.random() == r_py, "r is not valid"
        assert np.random.rand() == r_np, "Condition must be true"
        assert real_torch.rand(1).item() == r_torch, "Item must not be empty"
    finally:
        # Restore original torch in sys.modules
        if original_torch is not None:
            sys.modules["torch"] = original_torch
