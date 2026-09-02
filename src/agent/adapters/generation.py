"""Public generation-provider API."""

from __future__ import annotations

from .base_adapter import BaseGenerationProvider, GenerationRequest, GenerationResponse
from .factory import (
    GenerationProviderFactory,
    ProviderFactory,
    get_generation_provider,
    get_provider,
)
from .mock_adapter import MockGenerationProvider
from .openai_compatible_adapter import OpenAICompatibleGenerationProvider
from .spark_adapter import SparkGenerationProvider

__all__ = [
    "BaseGenerationProvider",
    "GenerationProviderFactory",
    "GenerationRequest",
    "GenerationResponse",
    "MockGenerationProvider",
    "OpenAICompatibleGenerationProvider",
    "ProviderFactory",
    "SparkGenerationProvider",
    "get_generation_provider",
    "get_provider",
]
