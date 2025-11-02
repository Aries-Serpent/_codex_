"""Determinism utilities for Codex ML workflows."""
from __future__ import annotations

import logging
import os
import random
from typing import Dict, Optional

try:  # pragma: no cover - optional dependency guards
    import numpy as np
except Exception:  # pragma: no cover
    np = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency guards
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore[assignment]

__all__ = ["set_deterministic", "set_cudnn_deterministic", "enable_determinism"]

logger = logging.getLogger(__name__)


def set_deterministic(seed: int = 42, deterministic: bool = True) -> None:
    """Configure Python, NumPy, and Torch for deterministic execution."""

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    if np is not None:
        np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        if hasattr(torch, "cuda"):
            try:
                torch.cuda.manual_seed_all(seed)  # type: ignore[call-arg]
            except Exception:  # pragma: no cover - optional CUDA path
                logger.debug("torch.cuda.manual_seed_all unavailable", exc_info=True)
        if deterministic:
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)
            except Exception:
                logger.debug("torch.use_deterministic_algorithms unavailable", exc_info=True)
            try:
                torch.backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                torch.backends.cudnn.benchmark = False  # type: ignore[attr-defined]
            except Exception:
                logger.debug("torch.backends.cudnn unavailable", exc_info=True)
            os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")


def set_cudnn_deterministic(enable: bool, benchmark: bool = False) -> None:
    """Toggle CuDNN deterministic and benchmark flags when Torch is available."""

    if torch is None:
        return
    try:
        backend = torch.backends.cudnn  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - backend unavailable
        logger.debug("torch.backends.cudnn missing", exc_info=True)
        return
    try:
        backend.deterministic = bool(enable)
        backend.benchmark = bool(benchmark)
        if enable and benchmark:
            logger.warning(
                "CUDNN determinism requested but benchmark=True may reintroduce non-determinism."
            )
    except Exception:  # pragma: no cover - device specific
        logger.debug("failed to set CuDNN determinism", exc_info=True)


def enable_determinism(
    *,
    seed: Optional[int] = None,
    deterministic: bool = True,
    num_threads: Optional[int] = None,
) -> Dict[str, object]:
    """Best-effort determinism shim retained for backward compatibility."""

    state: Dict[str, object] = {"seed": seed, "deterministic": bool(deterministic)}
    if num_threads is not None:
        state["num_threads"] = num_threads

    if seed is None:
        set_cudnn_deterministic(bool(deterministic), benchmark=not deterministic)
        return state

    set_deterministic(seed, deterministic=bool(deterministic))
    state.update(
        {
            "random": seed,
            "numpy": np is not None,
            "torch": torch is not None,
            "torch_cuda": bool(torch is not None and getattr(torch.cuda, "is_available", lambda: False)()),
        }
    )

    if torch is not None and num_threads is not None:
        try:
            torch.set_num_threads(int(num_threads))
            state["torch_num_threads"] = int(num_threads)
        except Exception:  # pragma: no cover - depends on build
            logger.debug("torch.set_num_threads unavailable", exc_info=True)

    if deterministic:
        set_cudnn_deterministic(True, benchmark=False)

    return state
