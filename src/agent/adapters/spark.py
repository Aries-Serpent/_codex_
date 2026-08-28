"""Compatibility layer for Spark providers."""

from .base_adapter import (
    BaseGenerationProvider,
    CompletionRequest,
    CompletionResponse,
    GenerationRequest,
    GenerationResponse,
)
from .spark_adapter import SparkAdapter, SparkGenerationProvider

__all__ = [
    "BaseGenerationProvider",
    "CompletionRequest",
    "CompletionResponse",
    "GenerationRequest",
    "GenerationResponse",
    "SparkAdapter",
    "SparkGenerationProvider",
]
