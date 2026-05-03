"""
RAG Embedding Providers Module

Provides multiple embedding provider implementations for offline and local model support.
"""

from typing import TYPE_CHECKING

from .gpt4all_provider import GPT4AllEmbeddingProvider
from .llamacpp_provider import LlamaCppEmbeddingProvider
from .ollama_provider import OllamaEmbeddingProvider

if TYPE_CHECKING:
    pass

__all__ = [
    "GPT4AllEmbeddingProvider",
    "LlamaCppEmbeddingProvider",
    "OllamaEmbeddingProvider",
]
