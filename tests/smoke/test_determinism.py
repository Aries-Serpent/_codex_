import os  # noqa: F401
import random

import pytest

from codex_ml.utils.determinism import enable_determinism

pytestmark = pytest.mark.smoke


def test_enable_determinism_repeats():
    s1 = enable_determinism(seed=123, deterministic=True, num_threads=1)
    nums1 = (random.randint(0, 10_000), random.randint(0, 10_000))

    s2 = enable_determinism(seed=123, deterministic=True, num_threads=1)
    nums2 = (random.randint(0, 10_000), random.randint(0, 10_000))

    assert nums1 == nums2
    # presence keys exist
    assert "torch" in s1 and "numpy" in s1
    assert "torch" in s2 and "numpy" in s2


def test_enable_determinism_cudnn_flags_toggle():
    """Test that CuDNN flags are properly toggled when deterministic changes."""
    torch = pytest.importorskip("torch")
    if not hasattr(torch.backends, "cudnn"):
        pytest.skip("CuDNN not available")

    # Enable determinism
    enable_determinism(seed=42, deterministic=True)
    assert torch.backends.cudnn.deterministic is True
    assert torch.backends.cudnn.benchmark is False

    # Disable determinism - flags should be reset
    enable_determinism(seed=42, deterministic=False)
    assert torch.backends.cudnn.deterministic is False
    assert torch.backends.cudnn.benchmark is True

    # Re-enable to verify toggle works both ways
    enable_determinism(seed=42, deterministic=True)
    assert torch.backends.cudnn.deterministic is True
    assert torch.backends.cudnn.benchmark is False
