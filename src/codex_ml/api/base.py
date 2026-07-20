"""Abstract base class for RAG API implementations.

This module provides the base interface for all RAG API implementations,
defining the contract that all concrete implementations must follow.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseRagAPI(ABC):
    """Abstract base class for RAG API implementations.

    Defines the interface for RAG operations including query, index, retrieve,
    and search functionality. All RAG API implementations should inherit from
    this class and implement the required methods.

    Attributes:
        name: Name identifier for this RAG API implementation
        config: Configuration dictionary for the RAG API
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        """Initialize the base RAG API.

        Args:
            name: Name identifier for this RAG API implementation
            config: Optional configuration dictionary for the RAG API
        """
        self.name = name
        self.config = config or {}

    @abstractmethod
    def query(self, query_text: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Execute a query against the RAG system.

        Args:
            query_text: The query text to search for
            top_k: Number of top results to return (default: 5)

        Returns:
            List of result dictionaries with relevance scores
        """

    @abstractmethod
    def index(self, documents: list[dict[str, Any]]) -> None:
        """Index a set of documents for retrieval.

        Args:
            documents: List of documents to index, each containing
                      'id', 'content', and optional metadata fields
        """

    @abstractmethod
    def retrieve(self, doc_ids: list[str]) -> list[dict[str, Any]]:
        """Retrieve documents by their IDs.

        Args:
            doc_ids: List of document IDs to retrieve

        Returns:
            List of retrieved documents
        """

    @abstractmethod
    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        """Perform semantic search using vector embeddings.

        Args:
            query_embedding: Vector embedding for the query
            top_k: Number of top results to return (default: 5)

        Returns:
            List of result dictionaries with similarity scores
        """

    def close(self) -> None:
        """Clean up resources used by the RAG API.

        This method is called when the RAG API is no longer needed.
        Subclasses should override this to release any resources.
        """
