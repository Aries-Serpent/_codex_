"""
Determinism utilities for reproducible ML experiments.

This module provides environment-based configuration for deterministic behavior
across random number generators, thread pools, and ML frameworks.
"""

import os
from typing import Any


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
        logger.warning(f"ImportError: {e}", exc_info=True)

    # Apply PyTorch settings if available
    try:
        import torch

        torch.manual_seed(seed)
        torch.set_num_threads(num_threads)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError as e:
        logger.warning(f"ImportError: {e}", exc_info=True)

    # Apply TensorFlow settings if available
    try:
        import tensorflow as tf

        tf.random.set_seed(seed)
        tf.config.threading.set_intra_op_parallelism_threads(num_threads)
        tf.config.threading.set_inter_op_parallelism_threads(num_threads)
    except ImportError as e:
        logger.warning(f"ImportError: {e}", exc_info=True)

    return {"determinism_enabled": True, "seed": seed, "num_threads": num_threads}


# Initialize on module import if environment variables are set
__determinism_summary = _init_determinism_from_env()
