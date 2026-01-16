"""
Interface Module

This module provides functionality for interface.

Usage:
    from embeddings.interface import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# Adapter interface for embedders
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
from abc import ABC, abstractmethod
from typing import Any


class EmbedderInterface(ABC):
    """
    Embedding provider interface.

    Implementations MUST be import-safe (no exception at import time when credentials absent).
    Provide synchronous `embed` for simplicity (worker can call in threadpool).
    """

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        raise NotImplementedError
