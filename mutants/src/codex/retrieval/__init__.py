"""Retrieval module for vector search and embedding."""

# Explicit imports to satisfy CodeQL py/undefined-export checks
# while maintaining lazy loading for optional dependencies
from .embed import EmbeddingModel, KnowledgeBaseLoader, build_embeddings
from .search import RetrievalEngine, search_knowledge_base
from .stores import FAISSStore, PGVectorStore, WeaviateStore

__all__ = [
    "EmbeddingModel",
    "FAISSStore",
    "KnowledgeBaseLoader",
    "PGVectorStore",
    "RetrievalEngine",
    "WeaviateStore",
    "build_embeddings",
    "search_knowledge_base",
]
