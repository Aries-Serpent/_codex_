"""Minimal torch.multiprocessing stub."""

from __future__ import annotations

from typing import Any


def get_context(*args: Any, **kwargs: Any) -> Any:
    return None


__all__ = ["get_context"]
