"""Deterministic dataset split utilities."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from typing import Any

from .split import train_val_test_split as _train_val_test_split

__all__ = [
    "SPLITS",
    "SplitDistribution",
    "assign_split",
    "stable_fold",
    "train_val_test_split",
]

SPLITS = ("train", "val", "test")


def stable_fold(example_id: str) -> int:
    """Return a stable fold value in the range [0, 99]."""

    if not isinstance(example_id, str):
        raise TypeError("example_id must be a string")
    digest = hashlib.sha256(example_id.encode("utf-8")).hexdigest()
    return int(digest, 16) % 100


def assign_split(example_id: str) -> str:
    """Assign a deterministic split name based on ``example_id``."""

    fold = stable_fold(example_id)
    if fold < 80:
        return "train"
    if fold < 90:
        return "val"
    return "test"


class SplitDistribution(dict[str, Any]):
    """Helper to summarise split distributions for diagnostics."""

    def __init__(self, counts: Mapping[str, int] | None = None) -> None:
        super().__init__({split: 0 for split in SPLITS})
        if counts:
            for split, count in counts.items():
                if split not in SPLITS:
                    raise KeyError(f"Unknown split '{split}'")
                self[split] = int(count)

    @classmethod
    def from_ids(cls, example_ids: Iterable[str]) -> SplitDistribution:
        counts = {split: 0 for split in SPLITS}
        for example_id in example_ids:
            split = assign_split(example_id)
            counts[split] += 1
        return cls(counts)

    def total(self) -> int:
        return sum(self.values())

    def proportions(self) -> dict[str, float]:
        total = self.total() or 1
        return {split: self[split] / total for split in SPLITS}


def train_val_test_split(
    dataset,
    val_frac: float = 0.1,
    test_frac: float = 0.1,
    seed: int = 0,
    **kwargs,
):
    """Backward-compatible shim for legacy callers."""

    return _train_val_test_split(
        dataset,
        val_frac=val_frac,
        test_frac=test_frac,
        seed=seed,
        **kwargs,
    )


__docformat__ = "restructuredtext"
