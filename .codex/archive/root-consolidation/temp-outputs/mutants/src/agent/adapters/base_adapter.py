"""
Base Adapter - Interface for AI provider adapters.

This module defines the base interface that all AI provider adapters must implement.

Author: Copilot Agent
Generated: 2025-12-24
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class CompletionRequest:
    """Request for a completion from an AI provider."""

    prompt: str
    system_prompt: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.7
    tools: list[dict[str, Any]] | None = None
    model: str | None = None


@dataclass
class CompletionResponse:
    """Response from an AI provider."""

    content: str
    model: str
    usage: dict[str, int]
    tool_calls: list[dict[str, Any]] | None = None
    finish_reason: str = "stop"


class BaseAdapter(ABC):
    """Base interface for AI provider adapters.

    All adapter implementations must inherit from this class and
    implement the required methods.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the AI provider."""

    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a completion for the given request.

        Args:
            request: The completion request.

        Returns:
            The completion response.
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the adapter is healthy and can make requests.

        Returns:
            True if healthy, False otherwise.
        """

    def get_default_model(self) -> str:
        """Return the default model for this provider."""
        return "default"

    def estimate_cost(self, usage: dict[str, int]) -> float:
        """Estimate the cost of a request based on usage.

        Args:
            usage: Token usage dictionary.

        Returns:
            Estimated cost in USD.
        """
        return 0.0
