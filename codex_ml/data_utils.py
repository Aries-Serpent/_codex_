"""Dataset helpers for HuggingFace trainer integration."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

try:  # pragma: no cover - datasets optional
    from datasets import Dataset
except Exception:  # pragma: no cover - fallback minimal dataset
    from training.engine_hf_trainer import Dataset  # type: ignore

__all__ = ["split_dataset"]


def split_dataset(dataset: Dataset, *, val_split: float = 0.1) -> Tuple[Dataset, Dataset]:
    if not 0.0 < val_split < 1.0:
        raise ValueError("val_split must be between 0 and 1")
    length = len(dataset)
    val_size = max(1, int(length * val_split))
    train_size = length - val_size
    train = dataset.select(range(train_size)) if hasattr(dataset, "select") else dataset
    val = dataset.select(range(train_size, length)) if hasattr(dataset, "select") else dataset
    return train, val
