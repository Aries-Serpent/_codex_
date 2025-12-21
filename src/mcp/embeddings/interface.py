# Adapter interface for embedders
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class EmbedderInterface(ABC):
    """
    Embedding provider interface.

    Implementations MUST be import-safe (no exception at import time when credentials absent).
    Provide synchronous `embed` for simplicity (worker can call in threadpool).
    """

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        raise NotImplementedError
