"""Reproducibility helpers."""

from __future__ import annotations

from pathlib import Path

from .checkpointing import set_seed as _set_seed

__all__ = ["set_seed", "set_reproducible"]


def set_seed(seed: int, *, deterministic: bool = True) -> None:
    _set_seed(seed, deterministic=deterministic)


def set_reproducible(seed: int, *, deterministic: bool = True) -> None:
    _set_seed(seed, deterministic=deterministic)
