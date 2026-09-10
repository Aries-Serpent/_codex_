"""Minimal torch.backends.cudnn stub."""

from __future__ import annotations

benchmark = False
deterministic = False


def __getattr__(name: str):
    if name in {"benchmark", "deterministic"}:
        return False
    raise AttributeError(f"module 'torch.backends.cudnn' has no attribute {name!r}")
