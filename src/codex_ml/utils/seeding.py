from __future__ import annotations

"""
Centralized, import-light helpers for reproducible and deterministic runs.
"""
import os
import random

from codex_ml.utils.determinism import set_deterministic as _apply_determinism


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
    except Exception:
        pass

    if deterministic:
        _apply_determinism(seed)


def set_deterministic(enabled: bool = True, *, seed: int | None = None) -> None:
    """Re-assert deterministic toggles using the shared helper."""

    if not enabled:
        return
    _apply_determinism(seed or 0)


__all__ = ["set_reproducible", "set_deterministic"]
