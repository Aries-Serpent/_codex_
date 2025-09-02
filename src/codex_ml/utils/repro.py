from __future__ import annotations

import os
import random

import numpy as np
import torch


def set_reproducible(seed: int = 42) -> None:
    """Best-effort determinism: seeds, deterministic algorithms, cuDNN & cuBLAS guards.
    See PyTorch notes for guarantees and limitations.
    """
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


__all__ = ["set_reproducible"]
