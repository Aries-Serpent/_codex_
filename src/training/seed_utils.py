"""
Seed Utils Module

This module provides functionality for seed utils.

Usage:
    from training.seed_utils import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import os  # noqa: E402
import random  # noqa: E402
from typing import Any  # noqa: E402

try:
    import numpy as np
except ImportError:  # pragma: no cover - numpy is optional
    np = None


def _set_numpy_seed(seed: int) -> None:
    if np is None:
        return
    try:
        np.random.seed(seed)
    except (AttributeError, RuntimeError):
        # numpy can raise when compiled without RNG support
        logger.debug("Suppressed exception in handler", exc_info=True)


def _set_torch_seed(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            logger.debug("Suppressed exception in handler", exc_info=True)
        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)
            except TypeError as e:
                type(e).__name__
                logger.debug("TypeError: <ERROR_TYPE>")
                logger.warning("TypeError: <ERROR_TYPE>", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)
            except AttributeError as e:
                type(e).__name__
                logger.debug("AttributeError: <ERROR_TYPE>")
                logger.warning("AttributeError: <ERROR_TYPE>", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def set_all_seeds(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    # Always set PYTHONHASHSEED to ensure reproducibility
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


__all__ = ["set_all_seeds"]
