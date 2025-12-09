"""
Deterministic data splitting utilities for reproducible experiments.

Provides functions to split datasets into train/val/test sets with
guaranteed determinism and reproducibility.
"""

from typing import List, Tuple

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


def split_indices(
    n: int,
    train_ratio: float,
    val_ratio: float,
    seed: int = 42,
) -> Tuple[List[int], List[int], List[int]]:
    """
    Split indices deterministically into train/val/test sets.

    Args:
        n: Total number of samples
        train_ratio: Proportion for training (0.0 to 1.0)
        val_ratio: Proportion for validation (0.0 to 1.0)
        seed: Random seed for reproducibility

    Returns:
        Tuple of (train_indices, val_indices, test_indices)

    Example:
        >>> train, val, test = split_indices(1000, 0.8, 0.1, seed=42)
        >>> len(train), len(val), len(test)
        (800, 100, 100)

    Note:
        - Uses NumPy's default_rng if available, otherwise falls back to Python random
        - All indices appear exactly once across all splits
        - Deterministic: same seed always produces same split within the same backend
        - WARNING: NumPy and Python random use different RNG algorithms, so the same
          seed will produce different splits depending on whether NumPy is installed.
          For cross-platform reproducibility, ensure NumPy is available in all environments.
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
