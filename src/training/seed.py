"""Utilities for establishing deterministic seeds in lightweight training loops.

PHASE 3 HARDENING: Enhanced exception handling with logging instead of silent pass.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

_DEFAULT_SEED = 42


def _set_seed(seed: int, *, deterministic: bool = True) -> None:
    """Set random seed. Tries codex_ml implementation, falls back to basic torch/numpy.
    
    This function uses lazy import to break circular dependencies with codex_ml.
    
    PHASE 3 HARDENING: All fallback paths now include logging instead of silent pass.
    """
    try:
        from codex_ml.utils.repro import set_seed as _codex_set_seed

        _codex_set_seed(seed, deterministic=deterministic)
    except (ImportError, AttributeError, TypeError) as e:
        # Fallback if codex_ml not available or has different signature
        logger.debug(f"codex_ml not available, using fallback seed methods: {e}")
        
        # PHASE 3 HARDENING: Log failures instead of silent pass
        try:
            import random

            random.seed(seed)
        except Exception as e:  # noqa: BLE001 - Broad exception for robustness
            logger.warning(f"Failed to set Python random seed: {e}")
        
        try:
            import numpy as np

            np.random.seed(seed)
        except Exception as e:  # noqa: BLE001 - Broad exception for robustness
            logger.warning(f"Failed to set NumPy random seed: {e}")
        
        try:
            import torch

            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            if deterministic:
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False
        except Exception as e:  # noqa: BLE001 - Broad exception for robustness
            logger.warning(f"Failed to set PyTorch seed: {e}")


def ensure_global_seed(seed: Optional[int] = None, *, deterministic: bool = True) -> int:
    """Resolve ``seed`` to an integer and propagate it via :func:`set_seed`.

    Parameters
    ----------
    seed:
        Optional user-provided seed. When ``None`` a sensible default is used so
        call sites can simply invoke :func:`ensure_global_seed()` to obtain a
        reproducible configuration.
    deterministic:
        When True, configures backends for deterministic behavior.

    Returns
    -------
    int
        The resolved seed value. Returning the seed makes it trivial for callers
        to persist the decision alongside checkpoints or logs.
    """

    resolved = int(seed) if seed is not None else _DEFAULT_SEED
    _set_seed(resolved, deterministic=deterministic)
    return resolved


__all__ = ["ensure_global_seed"]
