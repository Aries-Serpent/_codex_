"""Agent package for _codex_ autonomous agent system."""

from __future__ import annotations

from .adapters import (
    BaseAdapter,
    BaseGenerationProvider,
    CompletionRequest,
    CompletionResponse,
    GenerationProviderFactory,
    GenerationRequest,
    GenerationResponse,
    MockAdapter,
    MockGenerationProvider,
    OpenAICompatibleAdapter,
    OpenAICompatibleGenerationProvider,
    ProviderFactory,
    SparkAdapter,
    SparkGenerationProvider,
    get_generation_provider,
    get_provider,
)
from .core import AgentConfig, AgentCore
from .phase10 import Phase10Validator
from .secrets import GitHubSecretsManager

__all__ = [
    "AgentConfig",
    "AgentCore",
    "BaseAdapter",
    "BaseGenerationProvider",
    "CompletionRequest",
    "CompletionResponse",
    "GenerationProviderFactory",
    "GenerationRequest",
    "GenerationResponse",
    "GitHubSecretsManager",
    "MockAdapter",
    "MockGenerationProvider",
    "OpenAICompatibleAdapter",
    "OpenAICompatibleGenerationProvider",
    "Phase10Validator",
    "ProviderFactory",
    "SparkAdapter",
    "SparkGenerationProvider",
    "get_generation_provider",
    "get_provider",
]
