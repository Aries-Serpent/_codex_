"""Retrieval module for vector search and embedding."""

# Explicit imports to satisfy CodeQL py/undefined-export checks.
# Core symbols are always available; optional vector-store classes are only
# appended to __all__ when their backing library is installed.  This prevents
# the py/undefined-export alert that fires when __all__ contains a name that
# resolves to None (the fallback used by stores/__init__.py when dependencies
# are absent).
from .embed import EmbeddingModel, KnowledgeBaseLoader, build_embeddings
from .search import RetrievalEngine, search_knowledge_base
from .stores import FAISSStore, PGVectorStore, WeaviateStore

__all__ = [
    "EmbeddingModel",
    "KnowledgeBaseLoader",
    "RetrievalEngine",
    "build_embeddings",
    "search_knowledge_base",
]

# Optional stores: only exported via __all__ when the backing library is
# installed (i.e. the import did not fall back to None).
if FAISSStore is not None:
    __all__ = [*__all__, "FAISSStore"]
if PGVectorStore is not None:
    __all__ = [*__all__, "PGVectorStore"]
if WeaviateStore is not None:
    __all__ = [*__all__, "WeaviateStore"]
