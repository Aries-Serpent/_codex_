"""
Centralized, import-light helpers for reproducible and deterministic runs.
"""

from __future__ import annotations

import contextlib
import logging
import os
import random

logger = logging.getLogger(__name__)


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
        import numpy as np

        np.random.seed(seed)
        try:
            from codex_ml.utils.seed_registry import register_seed_snapshot

            register_seed_snapshot(numpy_state=np.random.get_state())
        except (ImportError, AttributeError):
            logger.debug("register_seed_snapshot unavailable; numpy seed set via np.random.seed()")
    except (ImportError, AttributeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    try:
        import torch

        torch.manual_seed(seed)
        if hasattr(torch, "cuda") and callable(getattr(torch.cuda, "manual_seed_all", None)):
            try:
                torch.cuda.manual_seed_all(seed)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
        try:
            backend = torch.backends.cudnn
            backend.deterministic = deterministic
            backend.benchmark = not deterministic
            if deterministic:
                os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":16:8")
                torch.use_deterministic_algorithms(True)
                matmul_backend = getattr(torch.backends, "cuda", None)
                if matmul_backend is not None:
                    matmul_backend.matmul.allow_tf32 = False
            else:
                with contextlib.suppress(Exception):
                    torch.use_deterministic_algorithms(False)
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    except (ImportError, AttributeError, ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning("Exception: <ERROR_TYPE>", exc_info=True)


def set_deterministic(enabled: bool = True) -> None:
    """
    Re-assert determinism toggles without changing global seed.
    Safe no-op when frameworks are absent.
    """
    try:
       import torch

       try:
           backend = torch.backends.cudnn
           backend.deterministic = enabled
           backend.benchmark = not enabled
       except (ValueError, TypeError, RuntimeError) as e:
           type(e).__name__
           logger.debug("Exception: <ERROR_TYPE>")
           logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    except (ImportError, AttributeError, ValueError, TypeError, RuntimeError) as e:
       type(e).__name__
       logger.debug("Exception: <ERROR_TYPE>")
       logger.warning("Exception: <ERROR_TYPE>", exc_info=True)


__all__ = ["set_deterministic", "set_reproducible"]
