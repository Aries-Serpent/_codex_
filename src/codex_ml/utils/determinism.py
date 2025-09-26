"""
Determinism utilities.

Provides opt-in helpers for enforcing additional GPU (CUDNN) determinism.
Intentionally lightweight and safe to import in environments without torch
or without CUDA support.

Typical usage (inside training loop setup):
    from codex_ml.utils.determinism import set_cudnn_deterministic
    set_cudnn_deterministic(True)

Notes:
- Enabling full determinism may reduce performance.
- Some CUDA ops may still be non-deterministic depending on driver / hardware.
"""

from __future__ import annotations

import logging
import os
import random
from typing import Dict

logger = logging.getLogger(__name__)


def set_cudnn_deterministic(enable: bool, benchmark: bool = False) -> None:
    """
    Enable or disable CUDNN deterministic behavior (if torch + CUDA available).

    Args:
        enable: If True sets torch.backends.cudnn.deterministic = True
        benchmark: Whether to leave benchmark enabled. For strict determinism
                   benchmark should usually be False. When enable=True and
                   benchmark=True a warning is logged.

    Behavior:
        - Silently no-ops if torch or CUDA is unavailable.
    """
    try:
        import torch  # noqa
    except Exception:
        return

    if not torch.cuda.is_available():
        return

    try:
        torch.backends.cudnn.deterministic = bool(enable)
        # Only set benchmark if explicitly passed; if enable True and benchmark True, warn.
        torch.backends.cudnn.benchmark = bool(benchmark)
        if enable and benchmark:
            logger.warning(
                "CUDNN determinism requested but benchmark=True may reintroduce non-determinism."
            )
    except Exception as e:  # noqa: broad-except
        logger.warning("Failed to configure CUDNN determinism: %s", e)


def _try_import_numpy():
    try:
        import numpy as np  # type: ignore

        return np
    except Exception:
        return None


def _try_import_torch():
    try:
        import torch  # type: ignore

        return torch
    except Exception:
        return None


def enable_determinism(
    seed: int = 42, deterministic: bool = True, num_threads: int = 1
) -> Dict[str, object]:
    """
    Enable a best-effort deterministic mode across Python, NumPy, and PyTorch.

    Args:
        seed: Global seed for Python/NumPy/Torch RNGs.
        deterministic: If True, request deterministic algorithms where supported.
        num_threads: If >0, set torch.set_num_threads(num_threads) when torch is available.

    Returns:
        A dictionary summary of what was configured (useful for logging).
    """

    summary: Dict[str, object] = {
        "seed": seed,
        "deterministic": deterministic,
        "num_threads": num_threads,
    }

    random.seed(seed)

    np = _try_import_numpy()
    if np is not None:
        np.random.seed(seed)
        summary["numpy"] = True
    else:
        summary["numpy"] = False

    torch = _try_import_torch()
    if torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            # For cuBLAS determinism (CUDA only). Safe to set even if not used.
            os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":16:8")
        if deterministic:
            try:
                torch.use_deterministic_algorithms(True)
            except Exception:
                # Torch < 1.8 or platform without the API - ignore gracefully
                summary["torch_use_deterministic_algorithms"] = "unavailable"
        set_cudnn_deterministic(bool(deterministic))
        summary["cudnn_deterministic"] = bool(deterministic)
        if num_threads and hasattr(torch, "set_num_threads"):
            try:
                torch.set_num_threads(int(num_threads))
            except Exception:
                pass
        summary["torch"] = True
        summary["torch_cuda"] = bool(torch.cuda.is_available())
    else:
        summary["torch"] = False
        summary["torch_cuda"] = False
        summary["cudnn_deterministic"] = False

    return summary


__all__ = ["enable_determinism", "set_cudnn_deterministic"]
