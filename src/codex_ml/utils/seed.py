"""Seed utilities for deterministic operations."""

from __future__ import annotations

import random
from typing import List, MutableSequence, Sequence, TypeVar

from codex_ml.utils.seeding import set_reproducible

T = TypeVar("T")


def set_seed(seed: int) -> None:
    """Synchronise RNG state across supported libraries.

    This function is a thin wrapper around :func:`codex_ml.utils.seeding.set_reproducible`
    that seeds Python's ``random`` module and, when available, NumPy and PyTorch.
    ``PYTHONHASHSEED`` is also pinned to guarantee deterministic hashing behaviour.
    """

    set_reproducible(seed, deterministic=True)


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


__all__ = ["deterministic_shuffle", "set_seed"]
