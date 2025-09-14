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
