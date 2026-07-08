"""RAG (Retrieval-Augmented Generation) package for _codex_."""

from __future__ import annotations

# Note: RAGPipeline, EmbeddingService, Chunker are not yet implemented as standalone classes
# The actual implementations are in the pipelines subpackage
from .pipelines import (
    ChunkingPipeline,
    EmbeddingPipeline,
    QuantumEnhancedRetrieval,
    QuantumRelevanceScorer,
    RetrievalPipeline,
)

__all__ = [
    "ChunkingPipeline",
    "EmbeddingPipeline",
    "QuantumEnhancedRetrieval",
    "QuantumRelevanceScorer",
    "RetrievalPipeline",
]
