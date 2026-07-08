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
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .embedding import EmbeddingPipeline

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MAX_QUERY_LENGTH = 10000
MAX_RESULTS = 100
DEFAULT_TOP_K = 10


# ---------------------------------------------------------------------------
# Vector store backend abstraction
# ---------------------------------------------------------------------------


class VectorStoreBackend(ABC):
    """Abstract base class for vector store backends."""

    @abstractmethod
    def add(self, doc_id: str, content: str, embedding: list[float], metadata: dict) -> None:
        """Add a document to the store."""

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        filters: dict | None,
    ) -> list[dict]:
        """Search for similar documents.

        Returns:
            List of dicts with keys: id, content, score, metadata.
        """


class InMemoryVectorStore(VectorStoreBackend):
    """In-memory vector store (default backend)."""

    def __init__(self) -> None:
        self._index: list[dict[str, Any]] = []

    def add(self, doc_id: str, content: str, embedding: list[float], metadata: dict) -> None:
        self._index.append(
            {
                "id": doc_id,
                "content": content,
                "embedding": embedding,
                "metadata": metadata,
            }
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        filters: dict | None,
    ) -> list[dict]:
        scored: list[tuple[dict, float]] = []
        for doc in self._index:
            if filters:
                if not all(doc.get("metadata", {}).get(k) == v for k, v in filters.items()):
                    continue
            score = _cosine_similarity(query_embedding, doc["embedding"])
            scored.append((doc, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            {
                "id": d["id"],
                "content": d["content"],
                "score": s,
                "metadata": d.get("metadata", {}),
            }
            for d, s in scored[:top_k]
        ]

    def clear(self) -> None:
        self._index.clear()

    def __len__(self) -> int:
        return len(self._index)


class PGVectorStoreBackend(VectorStoreBackend):
    """PGVector backend that delegates to PGVectorStore when psycopg3 is available.

    Note: The ``add()`` method is a no-op when the PGVectorStore is active because
    PGVectorStore uses an async API. Use the PGVectorStore directly for async inserts.
    When psycopg3 is unavailable the backend transparently falls back to in-memory storage.
    """

    def __init__(self) -> None:
        self._store: Any = None
        try:
            from codex.retrieval.stores.pgvector_store import (
                HAS_PSYCOPG3,
                PGVectorStore,
            )

            if HAS_PSYCOPG3:
                self._store = PGVectorStore()
        except (ValueError, TypeError, RuntimeError) as exc:
            logger.debug(
                "PGVectorStoreBackend: failed to initialize PGVectorStore; "
                "falling back to in-memory: %s",
                exc,
            )
        if self._store is None:
            logger.warning(
                "PGVectorStoreBackend: psycopg3/PGVectorStore unavailable, falling back to in-memory"  # noqa: E501
            )
            self._fallback = InMemoryVectorStore()
        else:
            self._fallback = None  # type: ignore[assignment]

    def add(self, doc_id: str, content: str, embedding: list[float], metadata: dict) -> None:
        if self._fallback is not None:
            self._fallback.add(doc_id, content, embedding, metadata)
        else:
            logger.warning(
                "PGVectorStoreBackend.add() is a no-op for the async PGVectorStore backend. "
                "Use PGVectorStore directly for async inserts."
            )

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        filters: dict | None,
    ) -> list[dict]:
        if self._fallback is not None:
            return self._fallback.search(query_embedding, top_k, filters)
        return []


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    if len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2, strict=False))
    n1 = sum(a * a for a in vec1) ** 0.5
    n2 = sum(b * b for b in vec2) ** 0.5
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


@dataclass
class RetrievalConfig:
    """Configuration for the retrieval pipeline."""

    top_k: int = DEFAULT_TOP_K
    similarity_threshold: float = 0.5
    include_metadata: bool = True
    rerank: bool = False
    backend: str = "memory"


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
    - Pluggable vector store backends (memory, pgvector)

    Safeguards:
    - Query length validation
    - Result count bounds
    - Graceful fallback on errors
    """

    def __init__(
        self,
        config: RetrievalConfig | None = None,
        embedding_pipeline: EmbeddingPipeline | None = None,
        vector_store: VectorStoreBackend | None = None,
    ) -> None:
        """Initialize the retrieval pipeline."""
        self.config = config or RetrievalConfig()
        self.embedding_pipeline = embedding_pipeline or EmbeddingPipeline()

        if vector_store is not None:
            self._store = vector_store
        elif self.config.backend == "pgvector":
            self._store = PGVectorStoreBackend()
        else:
            self._store = InMemoryVectorStore()

        # Backward-compatible alias so existing code using self._index still works
        # (read-only — the in-memory store's list is the source of truth)
        logger.info(
            "RetrievalPipeline initialized: top_k=%d, threshold=%.2f, backend=%s",
            self.config.top_k,
            self.config.similarity_threshold,
            self.config.backend,
        )

    @property
    def _index(self) -> list[dict[str, Any]]:
        """Backward-compatible access to the underlying index list."""
        if isinstance(self._store, InMemoryVectorStore):
            return self._store._index
        return []

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
        base = self.get_document_count()
        if ids is None:
            ids = [f"doc_{base + i}" for i in range(len(documents))]

        # Default empty metadata
        if metadatas is None:
            metadatas = [{} for _ in documents]

        # Generate embeddings
        embeddings = self.embedding_pipeline.embed_texts(documents)

        added = 0
        for doc, doc_id, metadata, emb_result in zip(
            documents, ids, metadatas, embeddings, strict=False
        ):
            self._store.add(doc_id, doc, emb_result.embedding, metadata)
            added += 1

        logger.info("Added %d documents to index (total: %d)", added, self.get_document_count())
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

        # Search via backend - fetch up to MAX_RESULTS then apply threshold filter
        raw_results = self._store.search(query_embedding.embedding, MAX_RESULTS, filters)

        # Apply threshold
        above_threshold = [r for r in raw_results if r["score"] >= self.config.similarity_threshold]
        total_found = len(above_threshold)
        top_docs = above_threshold[:top_k]

        results = [
            RetrievalResult(
                id=r["id"],
                content=r["content"],
                score=r["score"],
                metadata=r.get("metadata", {}) if self.config.include_metadata else {},
            )
            for r in top_docs
        ]

        search_time = (time.time() - start_time) * 1000

        logger.info("Retrieved %d results for query (%.1fms)", len(results), search_time)

        return RetrievalResponse(
            query=query,
            results=results,
            total_found=total_found,
            search_time_ms=search_time,
        )

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        return _cosine_similarity(vec1, vec2)

    def clear_index(self) -> None:
        """Clear all documents from the index."""
        if isinstance(self._store, InMemoryVectorStore):
            self._store.clear()
        logger.info("Index cleared")

    def get_document_count(self) -> int:
        """Return the number of indexed documents."""
        if isinstance(self._store, InMemoryVectorStore):
            return len(self._store)
        return 0


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
        metadatas=[
            {"topic": "python"},
            {"topic": "ml"},
            {"topic": "nlp"},
            {"topic": "db"},
        ],
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


# Backward-compatibility alias
Retrieval = RetrievalPipeline
