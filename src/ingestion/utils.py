"""Utility helpers for file operations, text reading, and deterministic shuffling.

This module provides a unified interface for file operations that combines:
- Text reading with automatic encoding detection
- Deterministic shuffling for reproducible data processing
- Backward-compatible wrappers for different API variants

Key functions:
- read_text_file: Backward-compatible text reading with encoding detection
- deterministic_shuffle: Reproducible shuffling using a seed
- seeded_shuffle: Alias for deterministic_shuffle (backward compatibility)
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import List, Sequence, TypeVar, Union

# Import text I/O helpers with fallback handling
try:
    from .io_text import read_text, _detect_encoding
except ImportError:
    # Provide minimal fallbacks if io_text module is not available
    def read_text(path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Fallback text reader."""
        return Path(path).read_text(encoding=encoding)
    
    def _detect_encoding(path: Path, sample_size: int = 131072) -> str:
        """Fallback encoding detector."""
        return "utf-8"

# Try to import seeded_shuffle from io_text if available
try:
    from .io_text import seeded_shuffle
except ImportError:
    # Define locally if not available in io_text
    def seeded_shuffle(seq: Sequence, seed: int) -> List:
        """Shuffle sequence deterministically using seed."""
        items = list(seq)
        rng = random.Random(seed)
        rng.shuffle(items)
        return items

T = TypeVar("T")

__all__ = [
    "read_text_file", 
    "deterministic_shuffle", 
    "seeded_shuffle", 
    "read_text", 
    "_detect_encoding"
]


def read_text_file(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Backward-compatible alias for text reading with encoding detection.

    This wrapper attempts to call the underlying `read_text` with an explicit
    encoding argument for backward compatibility with call sites that pass
    encoding. If the underlying implementation does not accept an `encoding`
    parameter (older variants), the wrapper will fall back to calling it
    without that argument.

    Parameters:
        path: File path to read
        encoding: Text encoding to use, or "auto" for detection

    Returns:
        File contents as string

    Raises:
        RuntimeError: If file reading fails after all fallback attempts
    """
    try:
        # Try with encoding parameter first (newer API)
        return read_text(path, encoding=encoding)
    except TypeError:
        # Underlying read_text may not accept an encoding parameter
        try:
            # Try without encoding parameter (older API)
            return read_text(path)
        except Exception as exc:
            raise RuntimeError(f"Failed to read text from {path!s}") from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to read text from {path!s}") from exc


def deterministic_shuffle(seq: Sequence[T], seed: int) -> List[T]:
    """Return a shuffled list using ``seed`` for determinism.

    This function provides reproducible shuffling by using a seeded random
    number generator. Useful for creating consistent train/test splits or
    data ordering across runs.

    Parameters:
        seq: Sequence to shuffle (list, tuple, etc.)
        seed: Random seed for reproducibility

    Returns:
        New list with shuffled elements

    Example:
        >>> items = [1, 2, 3, 4, 5]
        >>> shuffled = deterministic_shuffle(items, seed=42)
        >>> # Result will be the same every time with seed=42
    """
    items = list(seq)
    rng = random.Random(seed)
    rng.shuffle(items)
    return items


# Backward compatibility: ensure seeded_shuffle is available
# (some codebases may expect this name specifically)
if 'seeded_shuffle' not in globals():
    def seeded_shuffle(seq: Sequence[T], seed: int) -> List[T]:
        """Alias for deterministic_shuffle for backward compatibility."""
        return deterministic_shuffle(seq, seed)
