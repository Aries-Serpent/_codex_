"""Minimal torch.distributed stub."""

from __future__ import annotations

from typing import Any


class _Dist:
    @staticmethod
    def is_initialized() -> bool:
        return False

    @staticmethod
    def init_process_group(*args: Any, **kwargs: Any) -> None:
        return None

    @staticmethod
    def barrier(*args: Any, **kwargs: Any) -> None:
        return None


backend = _Dist()
init_process_group = backend.init_process_group
is_initialized = backend.is_initialized
barrier = backend.barrier

__all__ = ["backend", "init_process_group", "is_initialized", "barrier"]
