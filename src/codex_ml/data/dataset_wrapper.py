"""
Dataset Wrapper Module

This module provides functionality for dataset wrapper.

Usage:
    from data.dataset_wrapper import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import random  # noqa: E402
from collections.abc import Iterable  # noqa: E402

try:  # pragma: no cover - optional dependency
    from datasets import Dataset  # type: ignore[attr-defined]
except (ImportError, AttributeError):  # pragma: no cover - datasets missing
    Dataset = None

__all__ = ["DATASETS_AVAILABLE", "train_val_test_split"]

DATASETS_AVAILABLE = Dataset is not None


def _require_datasets() -> None:
    if not DATASETS_AVAILABLE:
        raise ImportError(
            "The 'datasets' package is required for codex_ml.data.dataset_wrapper. "
            "Install codex-ml[datasets] to enable this helper."
        )


def _validate_splits(splits: Iterable[float]) -> tuple[float, float, float]:
    values = tuple(float(s) for s in splits)
    if len(values) != 3:
        raise ValueError("splits must contain exactly three fractions")
    if any(v < 0 for v in values):
        raise ValueError("split fractions must be non-negative")
    total = sum(values)
    if abs(total - 1.0) > 1e-6:
        raise ValueError("split fractions must sum to 1.0")
    return values


def train_val_test_split(
    dataset: Dataset,
    *,
    seed: int = 42,
    splits: tuple[float, float, float] = (0.8, 0.1, 0.1),
) -> tuple[Dataset, Dataset, Dataset]:
    """Split a Hugging Face dataset deterministically."""

    _require_datasets()
    if not hasattr(dataset, "__len__"):
        raise TypeError("dataset must implement __len__")
    n_items = len(dataset)
    if n_items == 0:
        raise ValueError("dataset must contain at least one example")

    train_frac, val_frac, _test_frac = _validate_splits(splits)
    indices = list(range(n_items))
    rng = random.Random(int(seed))  # nosec B311 - deterministic dataset partitioning
    rng.shuffle(indices)

    train_end = int(n_items * train_frac)
    val_end = train_end + int(n_items * val_frac)

    if min(train_end, val_end - train_end, n_items - val_end) <= 0:
        raise ValueError("split fractions produce an empty subset; adjust ratios or dataset size")

    train_indices = indices[:train_end]
    val_indices = indices[train_end:val_end]
    test_indices = indices[val_end:]

    return (
        dataset.select(train_indices),
        dataset.select(val_indices),
        dataset.select(test_indices),
    )
