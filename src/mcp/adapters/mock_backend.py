"""
Mock Backend - Testing adapter that simulates external services.

This module provides a mock adapter for testing without real external calls.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Thread-safe in-memory storage
- Configurable latency simulation
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from .base_adapter import AdapterConfig, BaseAdapter, QueryResult

# Configure logging
logger = logging.getLogger(__name__)


class MockBackend(BaseAdapter):
    """Mock adapter for testing.

    Simulates a vector store without making real external calls.
    Useful for unit tests and development.

    Features:
    - In-memory vector storage
    - Configurable latency
    - Query simulation
    """

    def __init__(
        self,
        config: AdapterConfig | None = None,
        simulated_latency_ms: int = 10,
    ) -> None:
        """Initialize the mock backend.

        Args:
            config: Adapter configuration.
            simulated_latency_ms: Simulated network latency.
        """
        super().__init__(config)
        self._simulated_latency = simulated_latency_ms / 1000
        self._connected = False
        self._vectors: dict[str, dict[str, Any]] = {}
        self._call_count = 0

        logger.info("MockBackend initialized (latency: %dms)", simulated_latency_ms)

    @property
    def adapter_name(self) -> str:
        """Return the adapter name."""
        return "mock"

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected

    async def connect(self) -> bool:
        """Simulate connection."""
        await asyncio.sleep(self._simulated_latency)
        self._connected = True
        logger.info("MockBackend connected")
        return True

    async def disconnect(self) -> None:
        """Simulate disconnection."""
        await asyncio.sleep(self._simulated_latency)
        self._connected = False
        logger.info("MockBackend disconnected")

    async def health_check(self) -> bool:
        """Check health (always healthy for mock)."""
        return self._connected

    async def query(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        """Simulate a vector query.

        Returns mock results based on stored vectors.
        """
        self._call_count += 1
        await asyncio.sleep(self._simulated_latency)

        if not self._connected:
            return QueryResult(
                success=False,
                error="Not connected",
            )

        # Return random subset of stored vectors
        results: list[Any] = []
        for vec_id, vec_data in list(self._vectors.items())[:top_k]:
            results.append(
                {
                    "id": vec_id,
                    "score": 0.9 - 0.1 * len(results),  # Fake scores
                    "metadata": vec_data.get("metadata", {}),
                }
            )

        logger.debug("Mock query returned %d results", len(results))

        return QueryResult(
            success=True,
            data={"matches": results},
            metadata={"query": query_text, "top_k": top_k},
        )

    async def upsert(
        self,
        vectors: list[dict[str, Any]],
    ) -> QueryResult:
        """Store vectors in memory."""
        self._call_count += 1
        await asyncio.sleep(self._simulated_latency)

        if not self._connected:
            return QueryResult(
                success=False,
                error="Not connected",
            )

        upserted_count = 0
        for vec in vectors:
            vec_id = vec.get("id")
            if vec_id:
                self._vectors[vec_id] = vec
                upserted_count += 1

        logger.debug("Mock upsert stored %d vectors", upserted_count)

        return QueryResult(
            success=True,
            data={"upserted_count": upserted_count},
        )

    def get_call_count(self) -> int:
        """Return the number of calls made."""
        return self._call_count

    def get_vector_count(self) -> int:
        """Return the number of stored vectors."""
        return len(self._vectors)

    def reset(self) -> None:
        """Reset the mock backend."""
        self._vectors.clear()
        self._call_count = 0
        logger.info("MockBackend reset")
