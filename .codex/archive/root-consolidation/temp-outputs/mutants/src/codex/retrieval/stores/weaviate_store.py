"""
Weaviate Vector Store (Optional/Stub)
Disabled by default in local mode
"""

import logging
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class WeaviateStore:
    """Weaviate vector store (stub implementation for offline mode)"""

    def __init__(
        self,
        index_name: str = "default",
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.index_name = index_name
        self.url = url
        self.api_key = api_key
        logger.warning(
            "WeaviateStore is disabled in local/offline mode. "
            "Use FAISSStore for local vector search."
        )

    def create_index(self, embeddings: np.ndarray, documents: list[dict[str, Any]]) -> None:
        """Stub: Create index"""
        raise RuntimeError(
            "WeaviateStore is not available in offline mode. Use FAISSStore instead."
        )

    def save(self) -> None:
        """Stub: Save index"""
        raise RuntimeError(
            "WeaviateStore is not available in offline mode. Use FAISSStore instead."
        )

    def load(self) -> None:
        """Stub: Load index"""
        raise RuntimeError(
            "WeaviateStore is not available in offline mode. Use FAISSStore instead."
        )

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[dict[str, Any]]:
        """Stub: Search"""
        raise RuntimeError(
            "WeaviateStore is not available in offline mode. Use FAISSStore instead."
        )
