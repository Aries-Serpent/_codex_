"""Compatibility layer for OpenAI-compatible providers."""

from .base_adapter import (
    BaseGenerationProvider,
    CompletionRequest,
    CompletionResponse,
    GenerationRequest,
    GenerationResponse,
)
from .openai_compatible_adapter import (
    OpenAICompatibleAdapter,
    OpenAICompatibleGenerationProvider,
)

__all__ = [
    "BaseGenerationProvider",
    "CompletionRequest",
    "CompletionResponse",
    "GenerationRequest",
    "GenerationResponse",
    "OpenAICompatibleAdapter",
    "OpenAICompatibleGenerationProvider",
]
