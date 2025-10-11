"""Tests for deterministic seeding helpers."""

from __future__ import annotations

import importlib
import random
from contextlib import suppress

from codex_ml.utils.seed import set_seed


def _maybe_import(name: str):
    with suppress(Exception):
        return importlib.import_module(name)
    return None


def test_seed_repro():
    set_seed(123)
    assert random.randint(0, 100000) == 6863

    np = _maybe_import("numpy")
    if np is not None:
        set_seed(123)
        first_np = int(np.random.randint(0, 100000))
        set_seed(123)
        second_np = int(np.random.randint(0, 100000))
        assert second_np == first_np

    torch = _maybe_import("torch")
    if torch is not None and hasattr(torch, "randint"):
        set_seed(123)
        first_torch = int(torch.randint(0, 100000, (1,)).item())
        set_seed(123)
        second_torch = int(torch.randint(0, 100000, (1,)).item())
        assert second_torch == first_torch
