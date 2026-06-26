"""
Test Rng Reproducibility

Test module for rng reproducibility.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from codex_ml.training.rng_checkpoint import RNGState, set_seed


def test_rng_capture_and_restore(tmp_path: Path) -> None:
    torch = pytest.importorskip("torch")
    np = pytest.importorskip("numpy")

    set_seed(123)
    rng_state = RNGState()
    rng_state.capture()

    baseline = torch.rand(3)
    baseline_np = np.random.rand(3)
    baseline_py = random.random()

    restored = RNGState.load_from_file(rng_state.save_to_file(tmp_path / "rng.json"))
    restored.restore()

    assert torch.allclose(torch.rand(3), baseline)
    assert np.allclose(np.random.rand(3), baseline_np)
    assert random.random() == baseline_py, "r is not valid"

    next_value = random.random()
    restored.restore()
    assert random.random() == baseline_py, "r is not valid"
    assert random.random() == next_value, "Value must be initialized"


def test_set_seed_reproducible() -> None:
    torch = pytest.importorskip("torch")
    np = pytest.importorskip("numpy")

    set_seed(42)
    tensor_a = torch.rand(2)
    array_a = np.random.rand(2)

    set_seed(42)
    tensor_b = torch.rand(2)
    array_b = np.random.rand(2)

    assert torch.allclose(tensor_a, tensor_b)
    assert np.allclose(array_a, array_b)
