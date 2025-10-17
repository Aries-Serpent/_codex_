"""Tests for RNG state capture/restore utilities."""

from __future__ import annotations

import importlib
import importlib.util
import random

from codex_ml.utils import checkpoint_core

np = None
if importlib.util.find_spec("numpy") is not None:  # pragma: no cover - optional dependency
    np = importlib.import_module("numpy")

torch = None
_torch_has_rand = False
if importlib.util.find_spec("torch") is not None:  # pragma: no cover - optional dependency
    torch = importlib.import_module("torch")
    _torch_has_rand = hasattr(torch, "rand")


def test_rng_snapshot_restore_consistency() -> None:
    seed = 1234
    random.seed(seed)
    if np is not None:
        np.random.seed(seed)
    if torch is not None and _torch_has_rand:
        torch.manual_seed(seed)

    state = checkpoint_core.capture_rng_state()

    baseline_rand = [random.random() for _ in range(3)]  # noqa: S311
    baseline_np = np.random.random(3) if np is not None else None
    baseline_torch = torch.rand(3) if torch is not None and _torch_has_rand else None

    _ = [random.random() for _ in range(5)]  # noqa: S311
    if np is not None:
        _ = np.random.random(5)
    if torch is not None and _torch_has_rand:
        _ = torch.rand(5)

    checkpoint_core.restore_rng_state(state)

    assert [random.random() for _ in range(3)] == baseline_rand  # noqa: S311
    if np is not None and baseline_np is not None:
        assert np.allclose(np.random.random(3), baseline_np)
    if torch is not None and _torch_has_rand and baseline_torch is not None:
        result_torch = torch.rand(3)
        assert torch.allclose(result_torch, baseline_torch)
