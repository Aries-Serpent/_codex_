"""Adapters for connecting to external AI providers."""

from __future__ import annotations

from .base_adapter import (
    BaseAdapter,
    BaseGenerationProvider,
    CompletionRequest,
    CompletionResponse,
    GenerationRequest,
    GenerationResponse,
)
from .factory import (
    GenerationProviderFactory,
    ProviderFactory,
    get_generation_provider,
    get_provider,
)
from .mock_adapter import MockAdapter, MockGenerationProvider
from .openai_compatible_adapter import (
    OpenAICompatibleAdapter,
    OpenAICompatibleGenerationProvider,
)
from .spark_adapter import SparkAdapter, SparkGenerationProvider

__all__ = [
    "BaseAdapter",
    "BaseGenerationProvider",
    "CompletionRequest",
    "CompletionResponse",
    "GenerationRequest",
    "GenerationResponse",
    "GenerationProviderFactory",
    "MockAdapter",
    "MockGenerationProvider",
    "OpenAICompatibleAdapter",
    "OpenAICompatibleGenerationProvider",
    "ProviderFactory",
    "SparkAdapter",
    "SparkGenerationProvider",
    "get_generation_provider",
    "get_provider",
]
