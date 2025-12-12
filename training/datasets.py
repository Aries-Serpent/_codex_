"""
Legacy compatibility layer for datasets module.

DEPRECATED: Use src.training.datasets instead.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'training.datasets' is deprecated. "
    "Use 'src.training.datasets' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.training.datasets import (
    Dataset,
    IterableTextDataset,
    TextDataset,
    cache_texts,
    compute_dataset_hash,
    to_hf_dataset,
)

__all__ = [
    "Dataset",
    "IterableTextDataset",
    "TextDataset",
    "cache_texts",
    "compute_dataset_hash",
    "to_hf_dataset",
]
