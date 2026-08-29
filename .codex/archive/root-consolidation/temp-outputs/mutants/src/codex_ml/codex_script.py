"""
Determinism utilities for reproducible ML experiments.

This module provides environment-based configuration for deterministic behavior
across random number generators, thread pools, and ML frameworks.
"""

import logging
import os

logger = logging.getLogger(__name__)
from typing import Any  # noqa: E402


def _init_determinism_from_env() -> dict[str, Any]:
    """
    Initialize determinism settings from environment variables.

    Reads the following environment variables:
    - CODEX_DETERMINISM: Set to "1" to enable deterministic mode
    - CODEX_SEED: Random seed (default: 42)
    - CODEX_NUM_THREADS: Number of threads for deterministic operations (default: 1)

    Returns:
        dict: Configuration summary with keys:
            - determinism_enabled: bool
            - seed: int (if enabled)
            - num_threads: int (if enabled)

    Example:
        >>> import os
        >>> os.environ["CODEX_DETERMINISM"] = "1"
        >>> os.environ["CODEX_SEED"] = "123"
        >>> summary = _init_determinism_from_env()
        >>> assert summary["seed"] == 123
    """
    if os.getenv("CODEX_DETERMINISM") != "1":
        return {"determinism_enabled": False}

    seed = int(os.getenv("CODEX_SEED", "42"))
    num_threads = int(os.getenv("CODEX_NUM_THREADS", "1"))

    # Apply Python random seed
    import random

    random.seed(seed)

    # Apply NumPy seed if available
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)

    # Apply PyTorch settings if available
    try:
        import torch

        if hasattr(torch, "manual_seed"):
            torch.manual_seed(seed)
        if hasattr(torch, "set_num_threads"):
            torch.set_num_threads(num_threads)
        cuda = getattr(torch, "cuda", None)
        backends = getattr(torch, "backends", None)
        if cuda is not None and hasattr(cuda, "is_available") and cuda.is_available():
            if hasattr(cuda, "manual_seed_all"):
                cuda.manual_seed_all(seed)
            cudnn = getattr(backends, "cudnn", None) if backends is not None else None
            if cudnn is not None:
                cudnn.deterministic = True
                cudnn.benchmark = False
    except (ImportError, ModuleNotFoundError, OSError) as e:
        logger.debug("PyTorch determinism setup skipped: %s", e, exc_info=True)
    except AttributeError as e:
        logger.warning(
            "PyTorch determinism setup failed with unexpected error: %s", e, exc_info=True
        )
        raise

    # Apply TensorFlow settings if available
    try:
        import tensorflow as tf

        tf.random.set_seed(seed)
        tf.config.threading.set_intra_op_parallelism_threads(num_threads)
        tf.config.threading.set_inter_op_parallelism_threads(num_threads)
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)

    return {"determinism_enabled": True, "seed": seed, "num_threads": num_threads}


# Initialize on module import if environment variables are set
__determinism_summary = _init_determinism_from_env()
