"""
Test Repro Helper

Test module for repro helper.
"""
pytest.importorskip("numpy")
    torch = pytest.importorskip("torch")
import random
import numpy as np
from codex_ml.utils import set_reproducible







def test_set_reproducible_consistency():
    set_reproducible(123)
    py1 = random.random()
    np1 = np.random.rand()
    t1 = torch.rand(1)

    set_reproducible(123)
    py2 = random.random()
    np2 = np.random.rand()
    t2 = torch.rand(1)

    assert py1 == py2 and np1 == np2 and torch.allclose(t1, t2)
