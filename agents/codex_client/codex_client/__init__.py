"""Codex client utilities for the ITA bridge."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .bridge import CodexBridgeClient

__all__ = ["CodexBridgeClient"]


def __getattr__(name: str):
    if name == "CodexBridgeClient":
        from .bridge import CodexBridgeClient

        return CodexBridgeClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
