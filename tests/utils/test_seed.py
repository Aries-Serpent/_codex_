from __future__ import annotations

import importlib
import random

import pytest

from codex_ml.utils.seed import set_seed


def _optional_import(module: str):
    try:
        return importlib.import_module(module)
    except Exception:
        return None


@pytest.mark.parametrize("seed", [123, 42])
def test_seed_repro_python(seed: int) -> None:
    set_seed(seed)
    first = random.randint(0, 100000)
    set_seed(seed)
    second = random.randint(0, 100000)
    assert first == second
    if seed == 123:
        assert first == 6863


def test_seed_repro_numpy() -> None:
    np = _optional_import("numpy")
    if np is None:
        pytest.skip("numpy not installed")
    set_seed(123)
    first = np.random.randint(0, 100000)
    set_seed(123)
    second = np.random.randint(0, 100000)
    assert first == second == 15725


@pytest.mark.skipif(_optional_import("torch") is None, reason="torch not installed")
def test_seed_repro_torch() -> None:
    torch = importlib.import_module("torch")
    if not hasattr(torch, "rand"):
        pytest.skip("torch does not expose rand in this environment")
    set_seed(123)
    first = torch.rand(1).item()
    set_seed(123)
    second = torch.rand(1).item()
    assert first == second
