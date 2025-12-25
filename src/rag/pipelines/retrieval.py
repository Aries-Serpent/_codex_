"""
Retrieval Pipeline - Retrieve relevant documents from vector store.

This module provides retrieval functionality for the RAG pipeline.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Input validation on queries
- Bounds checking on result count
- Defensive error handling
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .embedding import EmbeddingPipeline

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MAX_QUERY_LENGTH = 10000
MAX_RESULTS = 100
DEFAULT_TOP_K = 10


@dataclass
class RetrievalConfig:
    """Configuration for the retrieval pipeline."""

    top_k: int = DEFAULT_TOP_K
    similarity_threshold: float = 0.5
    include_metadata: bool = True
    rerank: bool = False


@dataclass
class RetrievalResult:
    """A single retrieval result."""

    id: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResponse:
    """Response from a retrieval query."""

    query: str
    results: list[RetrievalResult]
    total_found: int
    search_time_ms: float = 0.0


class RetrievalPipeline:
    """
    Pipeline for retrieving relevant documents.

    Features:
    - Vector similarity search
    - Metadata filtering
    - Optional reranking
    - In-memory index for testing

    Safeguards:
    - Query length validation
    - Result count bounds
    - Graceful fallback on errors
    """

    def __init__(
        self,
        config: RetrievalConfig | None = None,
        embedding_pipeline: EmbeddingPipeline | None = None,
    ) -> None:
        """Initialize the retrieval pipeline."""
        self.config = config or RetrievalConfig()
        self.embedding_pipeline = embedding_pipeline or EmbeddingPipeline()

        # In-memory index for testing (production would use vector store)
        self._index: list[dict[str, Any]] = []

        logger.info(
            "RetrievalPipeline initialized: top_k=%d, threshold=%.2f",
            self.config.top_k,
            self.config.similarity_threshold
        )

    def add_documents(
        self,
        documents: list[str],
        ids: list[str] | None = None,
        metadatas: list[dict[str, Any]] | None = None,
    ) -> int:
        """
        Add documents to the index.

        Args:
            documents: List of document texts.
            ids: Optional document IDs.
            metadatas: Optional metadata for each document.

        Returns:
            Number of documents added.
        """
        if not documents:
            return 0

        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{len(self._index) + i}" for i in range(len(documents))]

        # Default empty metadata
        if metadatas is None:
            metadatas = [{} for _ in documents]

        # Generate embeddings
        embeddings = self.embedding_pipeline.embed_texts(documents)

        # Add to index
        added = 0
        for doc, doc_id, metadata, emb_result in zip(documents, ids, metadatas, embeddings):
            self._index.append({
                "id": doc_id,
                "content": doc,
                "embedding": emb_result.embedding,
                "metadata": metadata,
            })
            added += 1

        logger.info("Added %d documents to index (total: %d)", added, len(self._index))
        return added

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> RetrievalResponse:
        """
        Retrieve documents relevant to the query.

        Args:
            query: The search query.
            top_k: Number of results to return.
            filters: Optional metadata filters.

        Returns:
            RetrievalResponse with ranked results.
        """
        import time
        start_time = time.time()

        # Input validation (safeguard)
        if not query or not isinstance(query, str):
            return RetrievalResponse(
                query="",
                results=[],
                total_found=0,
            )

        # Truncate query (safeguard)
        if len(query) > MAX_QUERY_LENGTH:
            logger.warning("Query truncated: %d > %d", len(query), MAX_QUERY_LENGTH)
            query = query[:MAX_QUERY_LENGTH]

        # Bounds check on top_k (safeguard)
        top_k = top_k or self.config.top_k
        top_k = min(top_k, MAX_RESULTS)

        # Generate query embedding
        query_embedding = self.embedding_pipeline.embed_text(query)

        # Score all documents
        scored_docs = []
        for doc in self._index:
            # Apply filters if provided
            if filters:
                matches_filter = all(
                    doc.get("metadata", {}).get(k) == v
                    for k, v in filters.items()
                )
                if not matches_filter:
                    continue

            # Calculate cosine similarity
            score = self._cosine_similarity(
                query_embedding.embedding,
                doc["embedding"]
            )

            # Apply threshold
            if score >= self.config.similarity_threshold:
                scored_docs.append((doc, score))

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Take top_k
        top_docs = scored_docs[:top_k]

        # Build results
        results = [
            RetrievalResult(
                id=doc["id"],
                content=doc["content"],
                score=score,
                metadata=doc.get("metadata", {}) if self.config.include_metadata else {},
            )
            for doc, score in top_docs
        ]

        search_time = (time.time() - start_time) * 1000

        logger.info(
            "Retrieved %d results for query (%.1fms)",
            len(results),
            search_time
        )

        return RetrievalResponse(
            query=query,
            results=results,
            total_found=len(scored_docs),
            search_time_ms=search_time,
        )

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def clear_index(self) -> None:
        """Clear all documents from the index."""
        self._index.clear()
        logger.info("Index cleared")

    def get_document_count(self) -> int:
        """Return the number of indexed documents."""
        return len(self._index)


def main() -> None:
    """Test the retrieval pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = RetrievalPipeline()

    # Add some documents
    documents = [
        "Python is a programming language created by Guido van Rossum.",
        "Machine learning uses algorithms to learn from data.",
        "Natural language processing handles text analysis.",
        "Vector databases store embeddings for similarity search.",
    ]

    pipeline.add_documents(
        documents,
        metadatas=[{"topic": "python"}, {"topic": "ml"}, {"topic": "nlp"}, {"topic": "db"}],
    )

    # Query
    response = pipeline.retrieve("What is Python?", top_k=3)

    print(f"\nQuery: '{response.query}'")
    print(f"Found: {response.total_found} documents")
    print(f"Time: {response.search_time_ms:.1f}ms")
    print("\nResults:")
    for r in response.results:
        print(f"  [{r.score:.3f}] {r.content[:50]}...")


if __name__ == "__main__":
    main()
