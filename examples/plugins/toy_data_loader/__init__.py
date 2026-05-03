"""Toy data loader plugin returning a deterministic dataset."""

from __future__ import annotations

from collections.abc import Iterable
from typing import List


def build(data: Iterable[str] | None = None) -> list[str]:
    default = ("hello", "codex", "plugins")
    return list(data or default)


__all__ = ["build"]
