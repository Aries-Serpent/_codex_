"""Seed utilities for deterministic operations."""

from __future__ import annotations

import random
from typing import List, MutableSequence, Sequence, TypeVar

T = TypeVar("T")


def deterministic_shuffle(seq: Sequence[T], seed: int) -> List[T]:
    """Return a shuffled copy of *seq* using ``seed`` for randomness.

    The original sequence is left unmodified. A :class:`random.Random` instance
    seeded with ``seed`` performs the shuffling to ensure deterministic
    behaviour across runs.
    """

    items: MutableSequence[T] = list(seq)
    rng = random.Random(seed)
    rng.shuffle(items)
    return list(items)


__all__ = ["deterministic_shuffle"]
