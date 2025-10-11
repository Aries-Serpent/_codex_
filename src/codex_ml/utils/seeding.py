"""
Centralized, import-light helpers for reproducible and deterministic runs.
"""

import os
import random


def set_reproducible(seed: int | None = None, *, deterministic: bool = True) -> None:
    """
    Set a unified seed across Python, NumPy (if present), and Torch (if present).
    - Always sets PYTHONHASHSEED for hash stability.
    - Torch/CUDA and CuDNN determinism toggled if available.
    """

    if seed is None:
        seed = 0
    elif not isinstance(seed, int):  # pragma: no cover - developer misuse
        raise TypeError("seed must be an integer")

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    try:
        import numpy as np  # type: ignore

        np.random.seed(seed)  # type: ignore[attr-defined]
    except Exception:
        pass
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)  # type: ignore[attr-defined]
        if hasattr(torch, "cuda") and callable(getattr(torch.cuda, "manual_seed_all", None)):
            try:
                torch.cuda.manual_seed_all(seed)  # type: ignore[attr-defined]
            except Exception:
                pass
        try:
            backend = torch.backends.cudnn  # type: ignore[attr-defined]
            backend.deterministic = deterministic
            backend.benchmark = not deterministic
        except Exception:
            pass
    except Exception:
        pass


def set_deterministic(enabled: bool = True) -> None:
    """
    Re-assert determinism toggles without changing global seed.
    Safe no-op when frameworks are absent.
    """

    try:
        import torch  # type: ignore

        try:
            backend = torch.backends.cudnn  # type: ignore[attr-defined]
            backend.deterministic = enabled
            backend.benchmark = not enabled
        except Exception:
            pass
    except Exception:
        pass


__all__ = ["set_reproducible", "set_deterministic"]
