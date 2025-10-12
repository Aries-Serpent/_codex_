import random

from common.randomness import set_seed

try:
    import numpy as np
except Exception:
    np = None


def test_set_seed_python_random():
    s = set_seed(1234)
    assert s == 1234
    a = [random.random() for _ in range(5)]  # noqa: S311
    set_seed(1234)
    b = [random.random() for _ in range(5)]  # noqa: S311
    assert a == b


def test_set_seed_numpy_if_available():
    if np is None:
        return
    set_seed(2025)
    rs = np.random.RandomState(2025)
    set_seed(2025)
    assert abs(np.random.rand() - rs.rand()) < 1e-12
