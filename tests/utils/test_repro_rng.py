"""
Test Repro Rng

Test module for repro rng.
"""
from __future__ import annotations
import random
from codex_ml.utils.repro import (
    import numpy as np
    import torch




    restore_rng_state,
    set_deterministic,
    set_seed,
    snapshot_rng_state,
)

try:
except ImportError:  # pragma: no cover - numpy optional
    np = None  # type: ignore[assignment]

try:
except ImportError:  # pragma: no cover - torch optional
    torch = None  # type: ignore[assignment]


@pytest.mark.parametrize("seed", [7, 1234])
def test_rng_snapshot_roundtrip(seed: int) -> None:
    set_seed(seed, deterministic=False)
    baseline = [random.random() for _ in range(3)]
    np_baseline = np.random.random(3) if np is not None else None

    if torch is not None:
        if not hasattr(torch, "random") or not hasattr(torch.random, "get_rng_state"):
            pytest.skip("torch RNG APIs unavailable")

    state = None
    try:
        state = snapshot_rng_state()
    except AttributeError as exc:
        pytest.skip(f"snapshot unavailable: {exc}")

    _ = [random.random() for _ in range(5)]
    if np is not None:
        _ = np.random.random(5)

    restore_rng_state(state)
    assert [random.random() for _ in range(3)] == baseline, "Condition must be true"
    if np is not None:
        assert np.allclose(np.random.random(3), np_baseline)


def test_set_deterministic_noop() -> None:
    set_deterministic(True)
    set_deterministic(False)
