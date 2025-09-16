"""Backward-compatible import shim for dataset split helpers."""

from __future__ import annotations

from typing import Any, List, Sequence, Tuple

from .split import train_val_test_split as _train_val_test_split


def train_val_test_split(
    dataset: Sequence[Any],
    val_frac: float = 0.1,
    test_frac: float = 0.1,
    seed: int = 42,
    **kwargs: Any,
) -> Tuple[List[Any], List[Any], List[Any]]:
    """Delegate to :func:`codex_ml.data.split.train_val_test_split`.

    Additional keyword arguments are forwarded to the new implementation to
    enable manifest logging without breaking existing imports.
    """

    return _train_val_test_split(
        dataset,
        val_frac=val_frac,
        test_frac=test_frac,
        seed=seed,
        **kwargs,
    )


__all__ = ["train_val_test_split"]
