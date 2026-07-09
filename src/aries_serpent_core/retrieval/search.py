"""
Top-k Retrieval API
Per-tenant vector search using FAISS
"""

import logging
from pathlib import Path
from typing import Any, Optional

from .embed import EmbeddingModel
from .stores.factory import VectorStoreFactory

logger = logging.getLogger(__name__)


class RetrievalEngine:
    """Manages retrieval across multiple tenants"""

    def __init__(
        self,
        index_base_dir: str = ".codex/tenants",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
    ):
        self.index_base_dir = Path(index_base_dir)
        self.embedding_model_name = embedding_model
        self.cache_dir = cache_dir
        self.embedding_model = EmbeddingModel(embedding_model, cache_dir)
        self.tenant_stores: dict[str, Any] = {}

    def get_store(self, tenant_id: str, index_name: str = "default") -> Any:
        """Get or load the vector store for a tenant

        Args:
            tenant_id: Tenant identifier
            index_name: Index name

        Returns:
            Vector store instance
        """
        store_key = f"{tenant_id}:{index_name}"

        if store_key not in self.tenant_stores:
            # Create store via factory (DRQ-S81: use VectorStoreFactory instead of direct FAISSStore)  # noqa: E501
            index_dir = self.index_base_dir / tenant_id / "faiss"
            store = VectorStoreFactory.create(
                store_type="faiss",
                index_name=index_name,
                index_dir=str(index_dir),
            )

            # Try to load existing index
            try:
                store.load()
                logger.info(f"Loaded index for tenant {tenant_id}, index {index_name}")
            except FileNotFoundError as e:
                type(e).__name__
                logger.debug("FileNotFoundError: <ERROR_TYPE>")
                logger.warning("FileNotFoundError: <ERROR_TYPE>", exc_info=True)
                logger.warning(f"No index found for tenant {tenant_id}, index {index_name}")

            self.tenant_stores[store_key] = store

        return self.tenant_stores[store_key]

    def search(
        self,
        tenant_id: str,
        query: str,
        top_k: int = 5,
        index_name: str = "default",
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Search for relevant documents

        Args:
            tenant_id: Tenant identifier
            query: Search query text
            top_k: Number of results to return
            index_name: Index name to search
            filters: Optional metadata filters (not yet implemented)

        Returns:
            List of search results with documents and scores
        """
        # Get store
        store = self.get_store(tenant_id, index_name)

        if not store.index:
            logger.warning(f"No index available for tenant {tenant_id}")
            return []

        # Encode query
        query_vector = self.embedding_model.encode([query])[0]

        # Search
        results = store.search(query_vector, top_k)

        # Format results
        formatted_results = []
        for result in results:
            doc = result["document"]
            formatted_results.append(
                {
                    "document_id": doc.get("id", "unknown"),
                    "content": doc.get("content", ""),
                    "score": result["score"],
                    "metadata": doc.get("metadata", {}),
                }
            )

        logger.info(f"Retrieved {len(formatted_results)} results for tenant {tenant_id}")
        return formatted_results

    def build_index(
        self,
        tenant_id: str,
        documents: list[dict[str, Any]],
        index_name: str = "default",
        text_field: str = "content",
    ) -> None:
        """Build a new index for a tenant

        Args:
            tenant_id: Tenant identifier
            documents: List of document dictionaries
            index_name: Index name
            text_field: Field containing text content
        """
        if not documents:
            raise ValueError("No documents provided")

        # Extract text
        texts = [doc.get(text_field, "") for doc in documents]

        # Build embeddings
        logger.info(f"Building embeddings for {len(texts)} documents")
        embeddings = self.embedding_model.encode(texts, show_progress=True)

        # Create store
        index_dir = self.index_base_dir / tenant_id / "faiss"
        store = VectorStoreFactory.create(
            store_type="faiss",
            index_name=index_name,
            index_dir=str(index_dir),
        )

        # Create and save index
        store.create_index(embeddings, documents)
        store.save()

        # Cache the store
        store_key = f"{tenant_id}:{index_name}"
        self.tenant_stores[store_key] = store

        logger.info(f"Built index for tenant {tenant_id} with {len(documents)} documents")


def search_knowledge_base(
    tenant_id: str,
    query: str,
    top_k: int = 5,
    index_base_dir: str = ".codex/tenants",
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> list[dict[str, Any]]:
    """Convenience function for searching knowledge base

    Args:
        tenant_id: Tenant identifier
        query: Search query
        top_k: Number of results
        index_base_dir: Base directory for indexes
        embedding_model: Embedding model name

    Returns:
        List of search results
    """
    engine = RetrievalEngine(index_base_dir, embedding_model)
    return engine.search(tenant_id, query, top_k)
