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
import random
from typing import Dict, Optional

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


def enable_determinism(
    *,
    seed: Optional[int] = None,
    deterministic: bool = True,
    num_threads: Optional[int] = None,
) -> Dict[str, int]:
    """Best-effort determinism shim used across the codebase and tests."""

    state: Dict[str, int] = {}

    if seed is not None:
        random.seed(seed)
        state["random"] = seed

        try:
            import numpy as np  # type: ignore

            np.random.seed(seed)
        except Exception:  # pragma: no cover - optional dependency
            logger.debug("numpy unavailable for seeding", exc_info=True)
        finally:
            state["numpy"] = seed

        try:
            import torch  # type: ignore

            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)

            if num_threads is not None:
                try:
                    torch.set_num_threads(int(num_threads))
                except Exception:  # pragma: no cover - depends on build
                    logger.debug("torch.set_num_threads unavailable", exc_info=True)

            if deterministic:
                try:
                    torch.use_deterministic_algorithms(True)
                except Exception:
                    logger.debug(
                        "torch.use_deterministic_algorithms unavailable", exc_info=True
                    )
        except Exception:  # pragma: no cover - optional dependency
            logger.debug("torch unavailable for seeding", exc_info=True)
        finally:
            state["torch"] = seed

    set_cudnn_deterministic(bool(deterministic))
    return state


__all__ = ["set_cudnn_deterministic", "enable_determinism"]
