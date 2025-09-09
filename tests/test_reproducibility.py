import random

import numpy as np
import torch

from codex_ml.utils.repro import set_reproducible


def test_set_reproducible_reseeds_all():
    set_reproducible(123)
    r_py = random.random()
    r_np = np.random.rand()
    r_torch = torch.rand(1).item()

    set_reproducible(123)
    assert random.random() == r_py
    assert np.random.rand() == r_np
    assert torch.rand(1).item() == r_torch
