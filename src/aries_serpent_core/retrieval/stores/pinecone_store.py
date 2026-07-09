"""
Pinecone Vector Store (Optional/Stub)
Disabled by default in local mode
"""

import logging
from typing import Any, Optional

import numpy as np

from .base import VectorStore

logger = logging.getLogger(__name__)


class PineconeStore(VectorStore):
    """Pinecone vector store (stub implementation for offline mode)"""

    def __init__(
        self,
        index_name: str = "default",
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        dimension: Optional[int] = None,
    ):
        """Initialize Pinecone store (stub)

        Args:
            index_name: Name of the Pinecone index
            api_key: Pinecone API key
            environment: Pinecone environment (e.g., "us-west1-gcp")
            dimension: Vector dimension
        """
        self.index_name = index_name
        self.api_key = api_key
        self.environment = environment
        self.dimension = dimension

        logger.warning(
            "PineconeStore is disabled in local/offline mode. "
            "Use FAISSStore for local vector search."
        )

    def health_check(self) -> dict[str, Any]:
        """Health check (stub)"""
        return {
            "healthy": False,
            "backend": "pinecone",
            "reason": "Pinecone not available in offline mode",
        }

    def add(
        self,
        vectors: np.ndarray,
        metadata: Optional[list[dict[str, Any]]] = None,
        ids: Optional[list[str]] = None,
    ) -> list[str]:
        """Add vectors (stub)"""
        raise RuntimeError(
            "PineconeStore is not available in offline mode. Use FAISSStore instead."
        )

    def delete(self, ids: str | list[str]) -> int:
        """Delete vectors (stub)"""
        raise RuntimeError(
            "PineconeStore is not available in offline mode. Use FAISSStore instead."
        )

    def get(self, ids: str | list[str]) -> list[dict[str, Any]]:
        """Get vectors (stub)"""
        raise RuntimeError(
            "PineconeStore is not available in offline mode. Use FAISSStore instead."
        )

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Search (stub)"""
        raise RuntimeError(
            "PineconeStore is not available in offline mode. Use FAISSStore instead."
        )

    def count(self) -> int:
        """Count vectors (stub)"""
        return 0

    def clear(self) -> None:
        """Clear vectors (stub)"""
        raise RuntimeError(
            "PineconeStore is not available in offline mode. Use FAISSStore instead."
        )

    def save(self, path: Optional[str] = None) -> None:
        """Save index (stub)"""
        raise RuntimeError(
            "PineconeStore is not available in offline mode. Use FAISSStore instead."
        )

    def load(self, path: Optional[str] = None) -> None:
        """Load index (stub)"""
        raise RuntimeError(
            "PineconeStore is not available in offline mode. Use FAISSStore instead."
        )
