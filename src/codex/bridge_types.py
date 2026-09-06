"""Simple compatibility types for legacy `codex.bridge_types` imports."""

from __future__ import annotations

from enum import Enum


class BridgeType(str, Enum):
    HTTP = "http"
    WS = "ws"
    LOCAL = "local"

    def __new__(cls, value):
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj

    @classmethod
    def validate(cls, value):
        if value is None:
            raise TypeError("value cannot be None")
        try:
            return cls(str(value))
        except ValueError as exc:
            raise ValueError(f"Unsupported bridge type: {value!r}") from exc


__all__ = ["BridgeType"]
