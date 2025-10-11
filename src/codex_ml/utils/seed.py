"""Seed utilities for deterministic operations."""

from __future__ import annotations

import os
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


def set_seed(seed: int, *, deterministic: bool = True) -> None:
    """Synchronise RNG state across common numerical libraries."""

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    try:
        import numpy as np  # type: ignore[import-not-found]

        np.random.seed(seed)  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - optional dependency guard
        pass

    try:
        import torch  # type: ignore[import-not-found]

        torch.manual_seed(seed)  # type: ignore[attr-defined]
        if hasattr(torch, "cuda") and callable(getattr(torch.cuda, "manual_seed_all", None)):
            try:
                torch.cuda.manual_seed_all(seed)  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover - cuda optional
                pass
        try:
            backend = torch.backends.cudnn  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover - backend optional
            backend = None
        if backend is not None:
            try:
                backend.deterministic = deterministic
                backend.benchmark = not deterministic
            except Exception:  # pragma: no cover - backend guard
                pass
    except Exception:  # pragma: no cover - optional dependency guard
        pass


__all__ = ["deterministic_shuffle", "set_seed"]
