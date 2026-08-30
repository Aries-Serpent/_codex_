"""
Mock Adapter - Testing adapter that simulates AI responses.

This module provides a mock adapter for testing without making real API calls.

Author: Copilot Agent
Generated: 2025-12-24
"""

from __future__ import annotations

import time

from .base_adapter import BaseAdapter, CompletionRequest, CompletionResponse


class MockAdapter(BaseAdapter):
    """Mock adapter for testing.

    Simulates AI responses without making real API calls.
    Useful for unit tests and development.
    """

    def __init__(self, response_template: str = "Mock response: {prompt}") -> None:
        """Initialize the mock adapter.

        Args:
            response_template: Template for mock responses.
        """
        self._response_template = response_template
        self._call_count = 0
        self._latency_ms = 100

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "mock"

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def health_check(self) -> bool:
        """Always returns True for mock adapter."""
        return True

    def get_default_model(self) -> str:
        """Return the default mock model."""
        return "mock-model-v1"

    def get_call_count(self) -> int:
        """Return the number of calls made to this adapter."""
        return self._call_count

    def reset(self) -> None:
        """Reset the call counter."""
        self._call_count = 0

    def set_latency(self, ms: int) -> None:
        """Set simulated latency in milliseconds."""
        self._latency_ms = ms
