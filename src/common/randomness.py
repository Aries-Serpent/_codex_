from __future__ import annotations

import logging
import os
import random

logger = logging.getLogger(__name__)


try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None

try:
    import torch
except Exception:  # pragma: no cover
    torch = None


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
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        try:
            torch.backends.cudnn.deterministic = True  # type: ignore[attr-defined]
            torch.backends.cudnn.benchmark = False  # type: ignore[attr-defined]
        except Exception as exc:
            logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed
