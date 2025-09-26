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

from typing import Optional
import logging

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


__all__ = ["set_cudnn_deterministic"]