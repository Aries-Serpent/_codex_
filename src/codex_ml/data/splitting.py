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
        
    Warning:
        **Cross-platform reproducibility limitation**: NumPy and Python's random module
        use different RNG algorithms. The same seed will produce DIFFERENT splits depending
        on whether NumPy is installed. For true cross-platform reproducibility:
        
        - Option 1 (Recommended): Make NumPy a required dependency
        - Option 2: Always use the same RNG backend in all environments
        - Option 3: Accept different splits on different platforms
        
        Consider making NumPy required for this function if reproducibility across
        environments is critical for your use case.
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
