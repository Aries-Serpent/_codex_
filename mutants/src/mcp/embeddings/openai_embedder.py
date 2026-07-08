"""
Openai Embedder Module

This module provides functionality for openai embedder.

Usage:
    from embeddings.openai_embedder import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import importlib
import importlib.util
import logging
import os
from typing import Any

from .interface import EmbedderInterface

logger = logging.getLogger(__name__)


class OpenAIEmbedder(EmbedderInterface):
    """
    Minimal OpenAI embedder skeleton with lazy import.
    """

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self._client = None
        self._api_key = os.environ.get("OPENAI_API_KEY", "")

    def _ensure_client(self):
        if self._client:
            return
        if importlib.util.find_spec("openai") is None:
            logger.warning("openai package missing or cannot be imported")
            return
        client = importlib.import_module("openai")
        client.api_key = self._api_key
        self._client = client

    def embed(self, texts: list[str]) -> list[list[float]]:
        self._ensure_client()
        if not self._client:
            # Fallback: empty vectors to keep system safe
            return [[0.0] * 1 for _ in texts]
        resp = self._client.Embedding.create(model=self.model, input=texts)
        return [d["embedding"] for d in resp["data"]]

    def health_check(self) -> dict[str, Any]:
        ok = bool(self._api_key and self._client is not None)
        return {"status": "ok" if ok else "disconnected", "adapter": "openai"}
