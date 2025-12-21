import hashlib
from typing import Any, Dict, List

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
        vec = [((b & 0xFF) / 255.0) for b in h[: self.dim]]
        return vec

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self._text_to_vector(t) for t in texts]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "embedder": "mock", "dim": self.dim}
