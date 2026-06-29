"""
Randomness Module

This module provides functionality for randomness.

Usage:
    from common.randomness import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
import os
import random

logger = logging.getLogger(__name__)


try:
    import numpy as np
except (ImportError, AttributeError):  # pragma: no cover
    np = None

try:
    import torch
except (ImportError, AttributeError):  # pragma: no cover
    torch = None  # type: ignore[assignment]


def set_seed(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except (ImportError, AttributeError) as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except (
                        ImportError,
                        AttributeError,
                    ) as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True
                        backends.cudnn.benchmark = False
                    except (ValueError, TypeError, RuntimeError) as exc:
                        type(exc).__name__
                        logger.debug("Exception: <ERROR_TYPE>")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed
