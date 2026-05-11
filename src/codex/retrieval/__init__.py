"""Retrieval module for vector search and embedding."""

from importlib import import_module

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

_EXPORT_TO_MODULE = {
    "EmbeddingModel": ".embed",
    "KnowledgeBaseLoader": ".embed",
    "build_embeddings": ".embed",
    "RetrievalEngine": ".search",
    "search_knowledge_base": ".search",
    "FAISSStore": ".stores",
    "PGVectorStore": ".stores",
    "WeaviateStore": ".stores",
}


def __getattr__(name: str):
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(module_name, __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
