"""
Module: Vector Stores (stubs) (S-vector)

Offline-safe vector store stubs.
Provide light, introspection-friendly classes with informative errors
when real backends are not installed.
"""
from .pgvector_stub import PGVectorStore
from .weaviate_stub import WeaviateStore

__all__ = ["PGVectorStore", "WeaviateStore"]
