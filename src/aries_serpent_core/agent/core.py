"""Compatibility wrapper for the packaged agent core."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent.core import AgentConfig, AgentCore
else:
    try:
        from agent.core import AgentConfig, AgentCore
    except ImportError:  # pragma: no cover - fallback for legacy package layout
        from aries_serpent_core.agent.core import AgentConfig, AgentCore

__all__ = ["AgentConfig", "AgentCore"]
