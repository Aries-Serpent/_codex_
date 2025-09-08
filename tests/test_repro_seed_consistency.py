import random

import numpy as np
import torch

from codex_ml.utils.repro import set_reproducible


def test_set_reproducible_repeatable():
    set_reproducible(7)
    py1 = random.random()
    np1 = np.random.rand()
    t1 = torch.rand(1)

    set_reproducible(7)
    py2 = random.random()
    np2 = np.random.rand()
    t2 = torch.rand(1)

    assert py1 == py2
    assert np1 == np2
    assert torch.allclose(t1, t2)
