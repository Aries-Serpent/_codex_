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


def _seed_torch(seed: int, *, deterministic: bool = True) -> None:
    if torch is None:  # pragma: no cover - dependency missing
        return

    torch.manual_seed(seed)
    if hasattr(torch.cuda, "is_available") and torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    set_deterministic(deterministic)


def _enable_cublas_determinism() -> None:
    os.environ.setdefault(_CUBLAS_WORKSPACE_CONFIG, ":4096:8")


def _disable_cublas_determinism() -> None:
    os.environ.pop(_CUBLAS_WORKSPACE_CONFIG, None)


def set_reproducible(seed: int | None = None, *, deterministic: bool = True) -> None:
    """Seed core libraries for best-effort deterministic behaviour.

    The function synchronises the RNG state across Python, NumPy (when
    installed) and PyTorch (CPU and CUDA). When PyTorch is present we also try
    to enable deterministic algorithms and disable cuDNN benchmarking. These
    settings provide reproducibility for the majority of CPU workloads, but
    GPU kernels may still exhibit non-deterministic behaviour depending on the
    operations used and the underlying hardware.
    """

    if seed is None:
        seed = 0
    if not isinstance(seed, int):  # pragma: no cover - developer error
        raise TypeError("seed must be an integer")

    _set_pythonhashseed(seed)
    random.seed(seed)
    try:  # lazy import avoids module-level circular dependencies
        from codex_ml.utils import checkpointing as _ckpt_mod

        register = getattr(_ckpt_mod, "register_python_seed_state", None)
        if callable(register):
            register()
    except Exception:
        pass
    _seed_numpy(seed)
    _seed_torch(seed, deterministic=deterministic)
    if deterministic:
        _enable_cublas_determinism()
    else:
        _disable_cublas_determinism()


def set_deterministic(flag: bool, *, warn: bool = True) -> None:
    """Toggle PyTorch deterministic algorithms if available."""

    if torch is None:  # pragma: no cover - dependency missing
        return

    try:
        torch.backends.cudnn.deterministic = flag
        torch.backends.cudnn.benchmark = not flag
    except Exception:  # pragma: no cover - backend not available
        if warn:
            warnings.warn("cuDNN backend not available to toggle determinism", RuntimeWarning)

    use_deterministic = getattr(torch, "use_deterministic_algorithms", None)
    if callable(use_deterministic):
        try:
            use_deterministic(flag)
        except Exception as exc:  # pragma: no cover - runtime guard
            if warn:
                warnings.warn(
                    f"torch.use_deterministic_algorithms failed: {exc}",
                    RuntimeWarning,
                    stacklevel=2,
                )

    if flag and hasattr(torch, "cuda") and torch.cuda.is_available():
        _enable_cublas_determinism()
    elif not flag:
        _disable_cublas_determinism()


__all__ = ["set_reproducible", "set_deterministic"]
