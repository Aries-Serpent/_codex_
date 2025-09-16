"""Toy data loader plugin returning a deterministic dataset."""

from __future__ import annotations

from typing import Iterable, List


def build(data: Iterable[str] | None = None) -> List[str]:
    default = ("hello", "codex", "plugins")
    return list(data or default)


__all__ = ["build"]
