"""Deterministic seeding helpers."""

from __future__ import annotations

import os
import random
import warnings
from typing import Final

try:  # pragma: no cover - optional dependency
    import numpy as np
except Exception:  # pragma: no cover - numpy missing
    np = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - torch missing
    torch = None  # type: ignore[assignment]


_PYTHONHASHSEED: Final[str] = "PYTHONHASHSEED"
_CUBLAS_WORKSPACE_CONFIG: Final[str] = "CUBLAS_WORKSPACE_CONFIG"


def _set_pythonhashseed(seed: int) -> None:
    os.environ[_PYTHONHASHSEED] = str(seed)


def _seed_numpy(seed: int) -> None:
    if np is None:  # pragma: no cover - dependency missing
        return
    np.random.seed(seed)


def _seed_torch(seed: int) -> None:
    if torch is None:  # pragma: no cover - dependency missing
        return

    torch.manual_seed(seed)
    if hasattr(torch.cuda, "is_available") and torch.cuda.is_available():
        os.environ.setdefault(_CUBLAS_WORKSPACE_CONFIG, ":16:8")
        torch.cuda.manual_seed_all(seed)

    try:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except Exception:  # pragma: no cover - backend not available
        pass

    use_deterministic = getattr(torch, "use_deterministic_algorithms", None)
    if callable(use_deterministic):
        try:
            use_deterministic(True)
        except Exception as exc:  # pragma: no cover - runtime guard
            warnings.warn(
                f"torch.use_deterministic_algorithms failed: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )


def set_reproducible(seed: int) -> None:
    """Seed core libraries for deterministic behaviour."""

    if not isinstance(seed, int):  # pragma: no cover - developer error
        raise TypeError("seed must be an integer")

    _set_pythonhashseed(seed)
    random.seed(seed)
    _seed_numpy(seed)
    _seed_torch(seed)


__all__ = ["set_reproducible"]
