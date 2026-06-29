"""
Pinecone Adapter Module

This module provides functionality for pinecone adapter.

Usage:
    from backends.pinecone_adapter import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# Pinecone adapter for MCP backend interface (skeleton + wiring to retries & metrics)
from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import sys
from collections.abc import Iterable
from typing import Any, Optional

from mcp.observability.metrics import Timer, increment

# Reuse Plan A scaffolds (import-safe)
from mcp.retries import retry_on_exception
from mcp.server.safety_checks import live_tests_enabled

from .interface import BackendAdapter, BackendResponse, VectorItem

logger = logging.getLogger(__name__)


class PineconeAdapter(BackendAdapter):
    """
    Pinecone adapter skeleton.

    - Lazy-imports pinecone SDK so import-time does not fail when package absent.
    - Uses retry_on_exception for transient network calls.
    - Emits minimal metrics via src/mcp/observability/metrics.
    - Guards live calls with live_tests_enabled() safety check.
    """

    def __init__(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def _lazy_import(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec("pinecone") is None:
            return None
        return importlib.import_module("pinecone")

    def connect(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except (ConnectionError, TimeoutError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    @retry_on_exception(tries=3)
    def _index_upsert(self, vectors: list, namespace: Optional[str] = None) -> Any:
        """Internal wrapper for index.upsert with retries."""
        if not self._index:
            raise RuntimeError("Index not initialized")
        return self._index.upsert(vectors=vectors, namespace=namespace)

    @retry_on_exception(tries=3)
    def _index_query(
        self,
        vector: list[float],
        top_k: int = 5,
        filter: Optional[dict] = None,
        namespace: Optional[str] = None,
    ) -> Any:
        if not self._index:
            raise RuntimeError("Index not initialized")
        return self._index.query(vector=vector, top_k=top_k, filter=filter, namespace=namespace)

    @retry_on_exception(tries=3)
    def _index_delete(self, ids: list[str], namespace: Optional[str] = None) -> Any:
        if not self._index:
            raise RuntimeError("Index not initialized")
        return self._index.delete(ids=ids, namespace=namespace)

    def upsert_batch(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except (ValueError, TypeError, RuntimeError):
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def query_top_k(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug(
                "ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety)."
            )
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(
                    vector=query_embedding,
                    top_k=top_k,
                    filter=filters,
                    namespace=namespace,
                )
        except (ValueError, TypeError, RuntimeError):
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": (
                            m.get("metadata", {}).get("content", "")
                            if isinstance(m.get("metadata", {}), dict)
                            else ""
                        ),
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def delete(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except (ConnectionError, TimeoutError):
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def health_check(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except (ConnectionError, TimeoutError):
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info
