"""Utility helpers for ingestion."""

from __future__ import annotations

import random
from typing import List, Sequence, TypeVar

T = TypeVar("T")

__all__ = ["deterministic_shuffle"]


def deterministic_shuffle(seq: Sequence[T], seed: int) -> List[T]:
    """Return a shuffled list using ``seed`` for determinism."""

    items = list(seq)
    rng = random.Random(seed)
    rng.shuffle(items)
    return items
