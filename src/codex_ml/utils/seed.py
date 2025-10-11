"""Seed utilities for deterministic operations."""

from __future__ import annotations

import os
import random
from collections.abc import MutableSequence, Sequence
from typing import TypeVar

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


def set_seed(seed: int) -> None:
    """Seed common RNG libraries for deterministic behaviour."""

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    try:
        import numpy as np  # type: ignore

        np.random.seed(seed)  # type: ignore[attr-defined]
    except Exception:
        pass
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)  # type: ignore[attr-defined]
        torch.cuda.manual_seed_all(seed)  # type: ignore[attr-defined]
        backends = getattr(torch, "backends", None)
        if backends is not None and hasattr(backends, "cudnn"):
            backends.cudnn.deterministic = True  # type: ignore[attr-defined]
            backends.cudnn.benchmark = False  # type: ignore[attr-defined]
    except Exception:
        pass


__all__ = ["deterministic_shuffle", "set_seed"]
