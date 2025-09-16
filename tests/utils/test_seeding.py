import os
import random

import pytest

from codex_ml.utils.seeding import set_reproducible

pytestmark = pytest.mark.skip(reason="Enable once CLI seeding integration is complete.")


def test_python_random_reseeding_matches() -> None:
    seed = 31415
    set_reproducible(seed)
    first = [random.random() for _ in range(3)]
    set_reproducible(seed)
    second = [random.random() for _ in range(3)]
    assert first == second


def test_numpy_random_reseeding_matches() -> None:
    np = pytest.importorskip("numpy")
    seed = 1618033
    set_reproducible(seed)
    first = np.random.random(5)
    set_reproducible(seed)
    second = np.random.random(5)
    assert np.allclose(first, second)


def test_torch_random_reseeding_matches() -> None:
    torch = pytest.importorskip("torch")
    seed = 271828
    set_reproducible(seed)
    first = torch.randn(4)
    set_reproducible(seed)
    second = torch.randn(4)
    assert torch.allclose(first, second)


def test_python_hash_seed_exported() -> None:
    seed = 9001
    set_reproducible(seed)
    assert os.environ.get("PYTHONHASHSEED") == str(seed)
