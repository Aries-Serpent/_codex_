"""Mock adapter for testing generation providers."""

from __future__ import annotations

import asyncio

from .base_adapter import (
    BaseGenerationProvider,
    CompletionRequest,
    CompletionResponse,
    GenerationRequest,
    GenerationResponse,
)


class MockGenerationProvider(BaseGenerationProvider):
    """Mock provider used in tests and as an offline fallback."""

    def __init__(self, response_template: str = "Mock response: {prompt}") -> None:
        self._response_template = response_template
        self._call_count = 0
        self._latency_ms = 100

    @property
    def provider_name(self) -> str:
        return "mock"

    async def complete(self, request: GenerationRequest) -> GenerationResponse:
        self._call_count += 1
        await asyncio.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return GenerationResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
            provider=self.provider_name,
        )

    async def health_check(self) -> bool:
        return True

    def get_default_model(self) -> str:
        return "mock-model-v1"

    def get_call_count(self) -> int:
        return self._call_count

    def reset(self) -> None:
        self._call_count = 0

    def set_latency(self, ms: int) -> None:
        self._latency_ms = ms


class MockAdapter(MockGenerationProvider):
    """Backward-compatible alias of the mock generation provider."""

    def __init__(self, response_template: str = "Mock response: {prompt}") -> None:
        super().__init__(response_template=response_template)


CompletionRequest = GenerationRequest
CompletionResponse = GenerationResponse
