"""Compatibility wrapper for the packaged agent core."""

from __future__ import annotations

try:
    from agent.core import AgentConfig, AgentCore
except ImportError:  # pragma: no cover - fallback for repo checkout or legacy path
    from src.agent.core import AgentConfig, AgentCore

__all__ = ["AgentConfig", "AgentCore"]
