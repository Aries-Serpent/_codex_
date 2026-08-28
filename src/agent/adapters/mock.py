"""Compatibility layer for mock providers."""

from .base_adapter import (
    BaseGenerationProvider,
    CompletionRequest,
    CompletionResponse,
    GenerationRequest,
    GenerationResponse,
)
from .mock_adapter import MockAdapter, MockGenerationProvider

__all__ = [
    "BaseGenerationProvider",
    "CompletionRequest",
    "CompletionResponse",
    "GenerationRequest",
    "GenerationResponse",
    "MockAdapter",
    "MockGenerationProvider",
]
