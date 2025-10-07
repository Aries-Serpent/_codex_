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
    _seed_numpy(seed)
    _seed_torch(seed, deterministic=deterministic)
    if deterministic:
        _enable_cublas_determinism()
    else:
        _disable_cublas_determinism()

    try:
        from codex_ml.utils import checkpointing as _checkpointing

        python_state = random.getstate()
        numpy_state = None
        if np is not None:
            try:
                numpy_state = np.random.get_state()
            except Exception:  # pragma: no cover - optional dependency guard
                numpy_state = None
        torch_state = None
        torch_cuda_state = None
        if torch is not None:
            try:
                torch_random = getattr(torch, "random", None)
                if torch_random is not None and hasattr(torch_random, "get_rng_state"):
                    torch_state = torch_random.get_rng_state().tolist()
                elif hasattr(torch, "get_rng_state"):
                    torch_state = torch.get_rng_state().tolist()
            except Exception:  # pragma: no cover - optional dependency guard
                torch_state = None
            if torch_state is not None:
                try:
                    if hasattr(torch, "cuda") and torch.cuda.is_available():
                        torch_cuda_state = [
                            state.tolist() for state in torch.cuda.get_rng_state_all()
                        ]
                except Exception:  # pragma: no cover - cuda optional
                    torch_cuda_state = None

        _checkpointing.register_seed_snapshot(
            python_state=python_state,
            numpy_state=numpy_state,
            torch_state=torch_state,
            torch_cuda_state=torch_cuda_state,
        )
    except Exception:  # pragma: no cover - checkpointing optional
        pass


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
