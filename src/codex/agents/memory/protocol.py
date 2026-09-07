"""Compatibility layer for the legacy ``codex.agents.memory.protocol`` import path."""

from aries_serpent_core.agents.memory.protocol import (  # noqa: F401
    MemoryEntry,
    MemoryProtocol,
    MemoryQuery,
)

__all__ = ["MemoryEntry", "MemoryProtocol", "MemoryQuery"]
