"""
Deterministic data splitting utilities for reproducible experiments.

Provides functions to split datasets into train/val/test sets with
guaranteed determinism and reproducibility.
"""

import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


def split_indices(
    n: int,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> Tuple[List[int], List[int], List[int]]:
    """Split indices into train/val/test sets.
    
    WARNING: Cross-Platform Reproducibility Limitation
    =================================================
    Results differ between NumPy and Python random backends.
    The same seed produces DIFFERENT splits depending on NumPy availability.
    
    For cross-environment reproducibility, choose ONE of:
    1. Ensure NumPy is consistently installed across all environments
    2. Use the pure Python fallback by setting CODEX_FORCE_PYTHON_RANDOM=1
    3. Implement a custom deterministic shuffle using a fixed algorithm
    
    Args:
        n: Number of indices
        train_ratio: Fraction for training (default: 0.8)
        val_ratio: Fraction for validation (default: 0.1)
        seed: Random seed for reproducibility
    
    Returns:
        Tuple of (train_indices, val_indices, test_indices)
        
    Example:
        >>> train, val, test = split_indices(1000, 0.8, 0.1, seed=42)
        >>> len(train), len(val), len(test)
        (800, 100, 100)
    """
    if not 0 <= train_ratio <= 1 or not 0 <= val_ratio <= 1:
        raise ValueError("Ratios must be between 0 and 1")

    if train_ratio + val_ratio > 1:
        raise ValueError("train_ratio + val_ratio cannot exceed 1.0")

    if NUMPY_AVAILABLE:
        rng = np.random.default_rng(seed)
        indices = np.arange(n)
        rng.shuffle(indices)
        indices_list = indices.tolist()
    else:
        # Fallback to Python random
        import random
        import warnings

        warnings.warn(
            "NumPy is not available. Falling back to Python's random module for splitting. "
            "This will produce DIFFERENT splits than NumPy for the same seed, "
            "which may break cross-platform reproducibility. "
            "Consider installing NumPy for consistent results: pip install numpy",
            UserWarning,
            stacklevel=2,
        )

        random.seed(seed)
        indices_list = list(range(n))
        random.shuffle(indices_list)

    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    train = indices_list[:train_end]
    val = indices_list[train_end:val_end]
    test = indices_list[val_end:]

    return train, val, test


__all__ = ["split_indices"]
