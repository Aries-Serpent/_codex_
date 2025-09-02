"""Deterministic configuration helpers."""

from __future__ import annotations

import os
import random

import numpy as np
import torch


def set_reproducible(seed: int = 42) -> None:
    """Seed common RNGs and enable deterministic algorithms."""

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    try:
        torch.use_deterministic_algorithms(True)
    except Exception:
        pass
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":16:8")
    try:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except Exception:
        pass
