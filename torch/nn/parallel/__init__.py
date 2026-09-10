"""Minimal torch.nn.parallel stub."""

from __future__ import annotations

from typing import Any


class DistributedDataParallel:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return args[0] if args else None


__all__ = ["DistributedDataParallel"]
