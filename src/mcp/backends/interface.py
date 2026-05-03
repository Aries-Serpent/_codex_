"""
Interface Module

This module provides functionality for interface.

Usage:
    from backends.interface import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# Adapter interface for MCP vector backends
# Minimal typed abstract base class used by adapters and tests.
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, Optional


class VectorItem(dict):
    """
    Minimal vector item representation:
    {
      "id": str,
      "embedding": list[float],
      "content": str,
      "metadata": dict[str, Any]
    }
    """


class BackendResponse(dict):
    """
    Query result item:
    {
      "id": str,
      "score": float,
      "content": str,
      "metadata": {...}
    }
    """


class BackendAdapter(ABC):
    """
    Abstract adapter interface that all vector DB adapters must implement.
    """

    @abstractmethod
    def connect(self) -> None:
        """Initialize connections/clients. Idempotent."""
        raise NotImplementedError()

    @abstractmethod
    def upsert_batch(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """Upsert a batch of vector items into namespace/tenant."""
        raise NotImplementedError()

    @abstractmethod
    def query_top_k(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        """Return top_k results with scores and metadata."""
        raise NotImplementedError()

    @abstractmethod
    def delete(self, namespace: str, id: str) -> bool:
        """Delete item by id; return True if deleted."""
        raise NotImplementedError()

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """Return backend health information (status, details)."""
        raise NotImplementedError()
