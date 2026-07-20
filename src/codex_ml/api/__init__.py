"""RAG API module for codex-ml.

This module provides the Retrieval-Augmented Generation (RAG) API interface
and implementations for semantic search and retrieval pipelines.

Exports:
    RagAPI: Core RAG API implementation
    BaseRagAPI: Abstract base class for RAG implementations
    RagAPIRegistry: Registry for RAG API implementations
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from .base import BaseRagAPI
from .rag_api import RagAPI
from .registry import RagAPIRegistry

__all__ = [
    "RagAPI",
    "BaseRagAPI",
    "RagAPIRegistry",
]
