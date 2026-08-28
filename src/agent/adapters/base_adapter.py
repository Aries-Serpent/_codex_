"""Base adapter contracts for generation providers.

This module defines the shared request/response contract used by the generated
provider implementations. The legacy ``CompletionRequest`` /
``CompletionResponse`` naming remains supported for compatibility with existing
agent code while the newer generation-oriented names are provided as the primary
API.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenerationRequest:
    """Normalized request payload passed to a generation provider."""

    prompt: str
    system_prompt: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.7
    tools: list[dict[str, Any]] | None = None
    model: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResponse:
    """Normalized response payload returned by a generation provider."""

    content: str
    model: str
    usage: dict[str, int]
    tool_calls: list[dict[str, Any]] | None = None
    finish_reason: str = "stop"
    provider: str | None = None
    raw: dict[str, Any] | None = None


# Backwards-compatible aliases used by pre-existing code/tests.
CompletionRequest = GenerationRequest
CompletionResponse = GenerationResponse


class BaseAdapter(ABC):
    """Base interface for AI provider adapters.

    All adapter implementations must inherit from this class and implement the
    required methods.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the AI provider."""

    @abstractmethod
    async def complete(self, request: GenerationRequest) -> GenerationResponse:
        """Generate a completion for the given request."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the adapter is healthy and can make requests."""

    def get_default_model(self) -> str:
        """Return the default model for this provider."""
        return "default"

    def estimate_cost(self, usage: dict[str, int]) -> float:
        """Estimate the cost of a request based on usage."""
        return 0.0


class BaseGenerationProvider(BaseAdapter):
    """Compatibility layer that makes generation providers explicit."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""

    async def complete(self, request: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError

    async def health_check(self) -> bool:
        raise NotImplementedError
