"""Seed utilities for deterministic operations.

This module now forwards seeding to centralized helpers in
codex_ml.utils.seeding to avoid duplication and drift.
"""

from __future__ import annotations

import random
from collections.abc import MutableSequence, Sequence
from typing import TypeVar

from codex_ml.utils.seeding import (
    set_deterministic as _set_deterministic,
    set_reproducible as _set_reproducible,
)

T = TypeVar("T")


def deterministic_shuffle(seq: Sequence[T], seed: int) -> list[T]:
    """Return a shuffled copy of *seq* using ``seed`` for randomness.

    The original sequence is left unmodified. A :class:`random.Random` instance
    seeded with ``seed`` performs the shuffling to ensure deterministic
    behaviour across runs.
    """

    items: MutableSequence[T] = list(seq)
    rng = random.Random(seed)
    rng.shuffle(items)
    return list(items)


def set_seed(seed: int, *, deterministic: bool = True) -> None:
    """Forward seeding to centralized helpers for deterministic behaviour."""

    _set_reproducible(seed, deterministic=deterministic)
    _set_deterministic(deterministic)


__all__ = ["deterministic_shuffle", "set_seed"]
