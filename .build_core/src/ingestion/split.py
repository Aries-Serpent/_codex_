"""Deterministic dataset splitting helpers."""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class SplitConfig:
    """Configuration controlling deterministic dataset splitting."""

    train_ratio: float = 0.8
    val_ratio: float = 0.1
    seed: int = 42

    def __post_init__(self) -> None:
        if not 0.0 <= self.train_ratio <= 1.0:
            raise ValueError("train_ratio must be within [0.0, 1.0]")
        if not 0.0 <= self.val_ratio <= 1.0:
            raise ValueError("val_ratio must be within [0.0, 1.0]")
        if self.train_ratio + self.val_ratio > 1.0:
            raise ValueError("train_ratio + val_ratio cannot exceed 1.0")


def split_files(
    files: Sequence[str], cfg: SplitConfig | None = None
) -> tuple[list[str], list[str], list[str]]:
    """Split file paths deterministically into train/val/test partitions."""

    cfg = SplitConfig() if cfg is None else cfg
    total = len(files)
    if total == 0:
        return [], [], []

    indices = list(range(total))
    rng = random.Random(cfg.seed)  # nosec B311 - deterministic file split
    rng.shuffle(indices)

    train_end = int(total * cfg.train_ratio)
    val_end = train_end + int(total * cfg.val_ratio)

    train_idx = indices[:train_end]
    val_idx = indices[train_end:val_end]
    test_idx = indices[val_end:]

    def _select(selected: list[int]) -> list[str]:
        return [files[i] for i in selected]

    return _select(train_idx), _select(val_idx), _select(test_idx)
