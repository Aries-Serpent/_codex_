"""
PostgreSQL pgvector Store (Optional/Stub)
Disabled by default in local mode
"""

import logging
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class PGVectorStore:
    """PostgreSQL pgvector store (stub implementation for offline mode)"""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string
        logger.warning(
            "PGVectorStore is disabled in local/offline mode. "
            "Use FAISSStore for local vector search."
        )
    
    def create_index(self, embeddings: np.ndarray, documents: list[dict[str, Any]]):
        """Stub: Create index"""
        raise NotImplementedError(
            "PGVectorStore is not available in offline mode. Use FAISSStore instead."
        )
    
    def save(self):
        """Stub: Save index"""
        raise NotImplementedError(
            "PGVectorStore is not available in offline mode. Use FAISSStore instead."
        )
    
    def load(self):
        """Stub: Load index"""
        raise NotImplementedError(
            "PGVectorStore is not available in offline mode. Use FAISSStore instead."
        )
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[dict[str, Any]]:
        """Stub: Search"""
        raise NotImplementedError(
            "PGVectorStore is not available in offline mode. Use FAISSStore instead."
        )
