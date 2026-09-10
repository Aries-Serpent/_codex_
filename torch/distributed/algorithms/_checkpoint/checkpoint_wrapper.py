"""Minimal activation checkpointing stub."""

from __future__ import annotations

from typing import Any


class CheckpointImpl:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


def apply_activation_checkpointing(*args: Any, **kwargs: Any) -> None:
    return None


def checkpoint_wrapper(*args: Any, **kwargs: Any) -> Any:
    return args[0] if args else None


__all__ = ["CheckpointImpl", "apply_activation_checkpointing", "checkpoint_wrapper"]
