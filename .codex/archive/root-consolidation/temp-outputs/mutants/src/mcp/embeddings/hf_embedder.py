"""
Hf Embedder Module

This module provides functionality for hf embedder.

Usage:
    from embeddings.hf_embedder import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import importlib
import importlib.util
import logging
from typing import Any

from .interface import EmbedderInterface

logger = logging.getLogger(__name__)


class HFEmbedder(EmbedderInterface):
    """
    Hugging Face embedder skeleton (sentence-transformers / transformers).
    Lazy-loads required model to avoid heavy imports in tests.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _ensure_model(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = importlib.import_module("sentence_transformers")
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        self._ensure_model()
        if not self._model:
            # safe fallback
            return [[0.0] * 1 for _ in texts]
        return self._model.encode(texts).tolist()

    def health_check(self) -> dict[str, Any]:
        return {
            "status": "ok" if self._model is not None else "disconnected",
            "adapter": "hf",
        }
