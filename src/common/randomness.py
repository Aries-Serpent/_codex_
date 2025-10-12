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
        try:
            manual_seed = getattr(torch, "manual_seed")
        except ImportError:
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except ImportError:
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            getattr(cuda_module, "manual_seed_all")(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except ImportError:
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed
