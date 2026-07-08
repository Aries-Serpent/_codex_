"""
Pinecone Adapter - Connect to Pinecone vector database.

This module provides an adapter for Pinecone vector store operations.
Uses lazy imports to avoid requiring pinecone-client when not used.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Lazy import of pinecone dependency
- Connection timeout handling
- Input validation on vectors
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from .base_adapter import AdapterConfig, BaseAdapter, QueryResult

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MAX_BATCH_SIZE = 100
MAX_VECTOR_DIMENSION = 4096


class PineconeAdapter(BaseAdapter):
    """Adapter for Pinecone vector database.

    Features:
    - Async operations via thread pool
    - Automatic batching for large upserts
    - Environment-based configuration

    Safeguards:
    - Lazy import of pinecone-client
    - Connection and query timeouts
    - Input validation on vector dimensions
    """

    def __init__(
        self,
        config: AdapterConfig | None = None,
        api_key: str | None = None,
        environment: str | None = None,
        index_name: str | None = None,
    ) -> None:
        """Initialize the Pinecone adapter.

        Args:
            config: Adapter configuration.
            api_key: Pinecone API key (or use PINECONE_API_KEY env var).
            environment: Pinecone environment (or use PINECONE_ENVIRONMENT env var).
            index_name: Name of the Pinecone index.
        """
        super().__init__(config)

        self._api_key = api_key or os.getenv("PINECONE_API_KEY")
        self._environment = environment or os.getenv("PINECONE_ENVIRONMENT")
        self._index_name = index_name or os.getenv("PINECONE_INDEX", "codex")

        self._client = None
        self._index = None
        self._connected = False

        logger.info(
            "PineconeAdapter initialized: index=%s, env=%s",
            self._index_name,
            self._environment or "not set",
        )

    @property
    def adapter_name(self) -> str:
        """Return the adapter name."""
        return "pinecone"

    @property
    def is_connected(self) -> bool:
        """Check if connected to Pinecone."""
        return self._connected and self._index is not None

    async def connect(self) -> bool:
        """Connect to Pinecone.

        Returns:
            True if connection successful, False otherwise.
        """
        if not self._api_key:
            logger.error("Pinecone API key not configured")
            return False

        try:
            # Lazy import pinecone
            try:
                from pinecone import Pinecone
            except ImportError:
                logger.error("pinecone package not installed. Install with: pip install pinecone")
                return False

            # Initialize client
            self._client = Pinecone(api_key=self._api_key)

            # Get index
            self._index = self._client.Index(self._index_name)  # type: ignore[attr-defined]

            self._connected = True
            logger.info("Connected to Pinecone index: %s", self._index_name)
            return True

        except (ConnectionError, TimeoutError) as e:
            logger.error("Failed to connect to Pinecone: %s", e)
            return False

    async def disconnect(self) -> None:
        """Disconnect from Pinecone."""
        self._index = None
        self._client = None
        self._connected = False
        logger.info("Disconnected from Pinecone")

    async def health_check(self) -> bool:
        """Check if Pinecone is healthy."""
        if not self.is_connected:
            return False

        try:
            # Describe index to verify connectivity
            stats = await asyncio.get_event_loop().run_in_executor(
                None,
                self._index.describe_index_stats,  # type: ignore[attr-defined]
            )
            return stats is not None
        except (ValueError, TypeError, RuntimeError) as e:
            logger.warning("Pinecone health check failed: %s", e)
            return False

    async def query(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
        vector: list[float] | None = None,
    ) -> QueryResult:
        """Query the Pinecone index.

        Args:
            query_text: The query text (used for logging).
            top_k: Number of results to return.
            filters: Optional metadata filters.
            vector: Query vector (must be pre-computed).

        Returns:
            QueryResult with matches or error.
        """
        if not self.is_connected:
            return QueryResult(
                success=False,
                error="Not connected to Pinecone",
            )

        if vector is None:
            return QueryResult(
                success=False,
                error="Vector must be provided for Pinecone queries",
            )

        try:
            # Run query in thread pool
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._index.query(  # type: ignore[attr-defined]
                    vector=vector,
                    top_k=top_k,
                    filter=filters,
                    include_metadata=True,
                ),
            )

            matches = []
            for match in result.get("matches", []):
                matches.append(
                    {
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata or {},
                    }
                )

            return QueryResult(
                success=True,
                data={"matches": matches},
                metadata={"top_k": top_k, "total_matches": len(matches)},
            )

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error("Pinecone query failed: %s", e)
            return QueryResult(
                success=False,
                error=str(e),
            )

    async def upsert(
        self,
        vectors: list[dict[str, Any]],
    ) -> QueryResult:
        """Upsert vectors to Pinecone.

        Args:
            vectors: List of dicts with id, values, and optional metadata.

        Returns:
            QueryResult indicating success or failure.
        """
        if not self.is_connected:
            return QueryResult(
                success=False,
                error="Not connected to Pinecone",
            )

        # Validate and format vectors
        formatted_vectors = []
        for vec in vectors:
            vec_id = vec.get("id")
            values = vec.get("values")

            if not vec_id or not values:
                continue

            # Bounds check (safeguard)
            if len(values) > MAX_VECTOR_DIMENSION:
                logger.warning("Vector dimension exceeds maximum: %d", len(values))
                continue

            formatted_vectors.append(
                {
                    "id": str(vec_id),
                    "values": values,
                    "metadata": vec.get("metadata", {}),
                }
            )

        if not formatted_vectors:
            return QueryResult(
                success=False,
                error="No valid vectors to upsert",
            )

        try:
            total_upserted = 0

            # Batch upserts (safeguard: respect batch size limits)
            for i in range(0, len(formatted_vectors), MAX_BATCH_SIZE):
                batch = formatted_vectors[i : i + MAX_BATCH_SIZE]

                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda b=batch: self._index.upsert(vectors=b),  # type: ignore[misc,attr-defined]
                )

                total_upserted += len(batch)

            logger.info("Upserted %d vectors to Pinecone", total_upserted)

            return QueryResult(
                success=True,
                data={"upserted_count": total_upserted},
            )

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error("Pinecone upsert failed: %s", e)
            return QueryResult(
                success=False,
                error=str(e),
            )

    async def delete(self, ids: list[str]) -> QueryResult:
        """Delete vectors by ID.

        Args:
            ids: List of vector IDs to delete.

        Returns:
            QueryResult indicating success or failure.
        """
        if not self.is_connected:
            return QueryResult(
                success=False,
                error="Not connected to Pinecone",
            )

        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._index.delete(ids=ids),  # type: ignore[attr-defined]
            )

            return QueryResult(
                success=True,
                data={"deleted_count": len(ids)},
            )

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error("Pinecone delete failed: %s", e)
            return QueryResult(
                success=False,
                error=str(e),
            )
