"""
Test Determinism

Test module for determinism.
"""

import random

import pytest

from codex_ml.utils.determinism import enable_determinism

pytestmark = pytest.mark.smoke


def test_enable_determinism_repeats():
    s1 = enable_determinism(seed=123, deterministic=True, num_threads=1)
    nums1 = (random.randint(0, 10_000), random.randint(0, 10_000))

    s2 = enable_determinism(seed=123, deterministic=True, num_threads=1)
    nums2 = (random.randint(0, 10_000), random.randint(0, 10_000))

    assert nums1 == nums2, "nums1 is not valid"
    # return contract is stable
    assert s1["seed"] == 123, "Condition must be true"
    assert s2["seed"] == 123, "Condition must be true"
    assert s1["deterministic"] is True, "Condition must be true"
    assert s2["deterministic"] is True, "Condition must be true"
    assert {"torch", "numpy", "random", "seed", "deterministic"} <= set(s1)
    assert {"torch", "numpy", "random", "seed", "deterministic"} <= set(s2)


def test_enable_determinism_seed_none_does_not_report_random_seed():
    state = enable_determinism(seed=None, deterministic=True)
    assert state["seed"] is None, "Condition must be true"
    assert state["deterministic"] is True, "Condition must be true"
    assert "random" not in state, "Condition must be true"


def test_enable_determinism_cudnn_flags_toggle():
    """Test that CuDNN flags are properly toggled when deterministic changes."""
    torch = pytest.importorskip("torch")
    if not hasattr(torch.backends, "cudnn"):
        pytest.skip("CuDNN not available")

    # Enable determinism
    enable_determinism(seed=42, deterministic=True)
    assert torch.backends.cudnn.deterministic is True, "deterministic is not valid"
    assert torch.backends.cudnn.benchmark is False, "benchmark is not valid"

    # Disable determinism - flags should be reset
    enable_determinism(seed=42, deterministic=False)
    assert torch.backends.cudnn.deterministic is False, "deterministic is not valid"
    assert torch.backends.cudnn.benchmark is True, "benchmark is not valid"

    # Re-enable to verify toggle works both ways
    enable_determinism(seed=42, deterministic=True)
    assert torch.backends.cudnn.deterministic is True, "deterministic is not valid"
    assert torch.backends.cudnn.benchmark is False, "benchmark is not valid"
