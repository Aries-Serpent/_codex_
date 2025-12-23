import logging
logger = logging.getLogger(__name__)
"""Utilities for establishing deterministic seeds across common libraries."""

from __future__ import annotations

import os
import random
from typing import Any, Dict

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover - numpy is optional
    np = None  # type: ignore


def _set_numpy_seed(seed: int) -> None:
    if np is None:
        return
    try:
        np.random.seed(seed)
    except (AttributeError, RuntimeError):
        # numpy can raise when compiled without RNG support
        pass


def _set_torch_seed(seed: int, deterministic: bool) -> Dict[str, Any]:
    torch_info: Dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
               logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
               logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
       logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def set_all_seeds(seed: int = 1337, deterministic: bool = True) -> Dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    Dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
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
