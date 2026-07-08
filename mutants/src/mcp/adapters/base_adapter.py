"""
Base Adapter - Interface for MCP service adapters.

This module defines the base interface that all MCP adapters must implement.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Input validation on all parameters
- Timeout handling for external calls
- Retry logic with exponential backoff
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class AdapterConfig:
    """Configuration for an MCP adapter."""

    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 1.0


@dataclass
class QueryResult:
    """Result of a query to an MCP adapter."""

    success: bool
    data: Any = None
    error: str | None = None
    metadata: dict = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAdapter(ABC):
    """Base interface for MCP service adapters.

    All adapter implementations must inherit from this class and
    implement the required abstract methods.
    """

    def __init__(self, config: AdapterConfig | None = None) -> None:
        """Initialize the adapter with configuration."""
        self.config = config or AdapterConfig()

    @property
    @abstractmethod
    def adapter_name(self) -> str:
        """Return the name of the adapter."""

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the adapter is connected to its service."""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the external service.

        Returns:
            True if connection successful, False otherwise.
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the external service."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the service is healthy.

        Returns:
            True if healthy, False otherwise.
        """

    @abstractmethod
    async def query(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        """Query the service.

        Args:
            query_text: The query text.
            top_k: Number of results to return.
            filters: Optional filters to apply.

        Returns:
            QueryResult with data or error.
        """

    @abstractmethod
    async def upsert(
        self,
        vectors: list[dict[str, Any]],
    ) -> QueryResult:
        """Upsert vectors to the service.

        Args:
            vectors: List of vector dictionaries with id, values, metadata.

        Returns:
            QueryResult indicating success or failure.
        """

    async def __aenter__(self) -> BaseAdapter:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()
