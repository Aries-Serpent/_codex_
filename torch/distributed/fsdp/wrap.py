"""Minimal wrap utilities stub for torch.distributed.fsdp.wrap."""

from __future__ import annotations

from typing import Any


def size_based_auto_wrap_policy(*args: Any, **kwargs: Any) -> Any:
    return None


def transformer_auto_wrap_policy(*args: Any, **kwargs: Any) -> Any:
    return None


__all__ = ["size_based_auto_wrap_policy", "transformer_auto_wrap_policy"]
