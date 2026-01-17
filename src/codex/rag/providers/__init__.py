"""
RAG Embedding Providers Module

Provides multiple embedding provider implementations for offline and local model support.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ollama_provider import OllamaEmbeddingProvider
    from .llamacpp_provider import LlamaCppEmbeddingProvider
    from .gpt4all_provider import GPT4AllEmbeddingProvider

__all__ = [
    "OllamaEmbeddingProvider",
    "LlamaCppEmbeddingProvider",
    "GPT4AllEmbeddingProvider",
]
