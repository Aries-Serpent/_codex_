"""Zendesk agent adapters for Codex agent core."""

from __future__ import annotations

import logging
from typing import Any

from agent.core import AgentConfig, AgentCore
from src.tools import (  # src. prefix needed: root ./tools/ shadows src/tools/
    ToolRegistry,
    get_registry,
)

logger = logging.getLogger(__name__)


class ZendeskAgentCore:
    """Zendesk-focused wrapper around the core AgentCore."""

    def __init__(
        self,
        config: AgentConfig | None = None,
        *,
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self.core = AgentCore(config=config)
        self.tool_registry = tool_registry or get_registry()
        self._sync_tools()
        logger.info("ZendeskAgentCore initialized")

    def _sync_tools(self) -> None:
        for tool in self.tool_registry.list_tools():
            self.core.register_tool(tool.name, tool.handler)

    def register_tool(self, name: str, handler: Any) -> None:
        """Register a tool with both the registry and core agent."""
        self.tool_registry.register(name, handler)
        self.core.register_tool(name, handler)

    def get_tool_names(self) -> list[str]:
        """Return tool names available to the agent."""
        return self.tool_registry.get_tool_names()


__all__ = ["AgentConfig", "AgentCore", "ZendeskAgentCore"]
