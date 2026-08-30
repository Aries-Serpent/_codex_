"""
Mock Embedder Module

This module provides functionality for mock embedder.

Usage:
    from embeddings.mock_embedder import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import hashlib
from typing import Any

from .interface import EmbedderInterface


class MockEmbedder(EmbedderInterface):
    """
    Deterministic mock embedder for local dev and CI.
    Produces fixed-size vectors derived from sha256 of the input text.
    """

    def __init__(self, dim: int = 16):
        self.dim = dim

    def _text_to_vector(self, t: str):
        h = hashlib.sha256(t.encode("utf-8")).digest()
        # Convert bytes -> floats in [0,1)
        return [((b & 0xFF) / 255.0) for b in h[: self.dim]]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._text_to_vector(t) for t in texts]

    def health_check(self) -> dict[str, Any]:
        return {"status": "ok", "embedder": "mock", "dim": self.dim}
