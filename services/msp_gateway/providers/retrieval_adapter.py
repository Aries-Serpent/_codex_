"""
Retrieval Adapter Interface
Provides abstraction for vector store retrieval
"""

import logging
from typing import Any, Dict, List, Optional

from codex.retrieval import RetrievalEngine

logger = logging.getLogger(__name__)


class RetrievalAdapter:
    """Adapter for retrieval operations"""

    def __init__(
        self,
        index_base_dir: str = ".codex/tenants",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
    ):
        self.engine = RetrievalEngine(
            index_base_dir=index_base_dir,
            embedding_model=embedding_model,
            cache_dir=cache_dir,
        )

    def query(
        self,
        tenant_id: str,
        query: str,
        top_k: int = 5,
        index_name: str = "default",
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Query the knowledge base

        Args:
            tenant_id: Tenant identifier
            query: Search query
            top_k: Number of results
            index_name: Index to search
            filters: Optional metadata filters

        Returns:
            List of search results
        """
        try:
            results = self.engine.search(
                tenant_id=tenant_id,
                query=query,
                top_k=top_k,
                index_name=index_name,
                filters=filters,
            )
            return results
        except Exception as e:
            logger.error(f"Error querying knowledge base for tenant {tenant_id}: {e}")
            return []

    def build_index(
        self,
        tenant_id: str,
        documents: List[Dict[str, Any]],
        index_name: str = "default",
        text_field: str = "content",
    ):
        """Build a new index for a tenant

        Args:
            tenant_id: Tenant identifier
            documents: List of documents
            index_name: Index name
            text_field: Field containing text
        """
        try:
            self.engine.build_index(
                tenant_id=tenant_id,
                documents=documents,
                index_name=index_name,
                text_field=text_field,
            )
            logger.info(f"Built index for tenant {tenant_id}")
        except Exception as e:
            logger.error(f"Error building index for tenant {tenant_id}: {e}")
            raise
