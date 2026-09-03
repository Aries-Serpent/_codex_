"""
GPT4All Embedding Provider

Provides embeddings using GPT4All local runtime.
"""

import logging
import weakref
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


def _finalize_embedder(embedder: object | None) -> None:
    """Best-effort cleanup for optional GPT4All resources.

    Explicit cleanup is preferred to destructor-based finalization because
    interpreter shutdown can leave global state partially torn down.
    """
    if embedder is None:
        return
    try:
        close = getattr(embedder, "close", None)
        if callable(close):
            close()
    except Exception:
        logger.debug("Failed to finalize GPT4All embedder", exc_info=True)

try:
    from gpt4all import Embed4All

    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False
    logger.debug("gpt4all not installed")


class GPT4AllEmbeddingProvider:
    """
    Embedding provider using GPT4All local runtime.

    GPT4All provides easy-to-use Python bindings for running local LLMs
    with bundled quantized models. This provider uses Embed4All for embeddings.

    Supported models:
    - nomic-embed-text-v1.5 (recommended, 768d)
    - all-MiniLM-L6-v2 (384d)
    - GPT4All bundled embedding models

    Example:
        >>> provider = GPT4AllEmbeddingProvider(model_name='nomic-embed-text-v1.5')
        >>> embeddings = provider.encode(['Hello world', 'Test document'])
        >>> logger.info(embeddings.shape)
        (2, 768)
    """

    def __init__(
        self,
        model_name: str = "nomic-embed-text-v1.5",
        dimension: Optional[int] = None,
    ):
        """
        Initialize GPT4All embedding provider.

        Args:
            model_name: Name of GPT4All embedding model
            dimension: Expected embedding dimension (auto-detected if None)
        """
        if not GPT4ALL_AVAILABLE:
            raise ImportError("gpt4all not installed. Install with: pip install gpt4all")

        self.model_name = model_name

        try:
            self.embedder = Embed4All()
            logger.info("Initialized GPT4All embedder")
            self._finalizer = weakref.finalize(self, _finalize_embedder, self.embedder)

            # Auto-detect dimension
            if dimension is None:
                test_embedding = self.embedder.embed("test")
                self.dimension = len(test_embedding)
                logger.debug(f"Detected embedding dimension: {self.dimension}")
            else:
                self.dimension = dimension

        except (ValueError, TypeError) as e:
            type(e).__name__
            logger.error("Failed to initialize GPT4All: <ERROR_TYPE>")
            raise

    def encode(
        self,
        texts: str | list[str],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> np.ndarray:
        """
        Generate embeddings for texts using GPT4All.

        Args:
            texts: Single text or list of texts to embed
            batch_size: Batch size for processing
            show_progress: Show progress bar (not implemented)

        Returns:
            numpy array of embeddings with shape (n, dimension)
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = []
        for text in texts:
            try:
                embedding = self.embedder.embed(text)
                embeddings.append(embedding)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.error("Error encoding text: <ERROR_TYPE>")
                embeddings.append([0.0] * self.dimension)

        return np.array(embeddings, dtype=np.float32)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension

    def __repr__(self) -> str:
        return f"GPT4AllEmbeddingProvider(model={self.model_name}, dim={self.dimension})"

    def close(self) -> None:
        """Close the optional embedder resource without relying on __del__."""
        finalizer = getattr(self, "_finalizer", None)
        if finalizer is not None and finalizer.alive:
            finalizer.detach()
        embedder = getattr(self, "embedder", None)
        try:
            if embedder is not None:
                close = getattr(embedder, "close", None)
                if callable(close):
                    close()
        except Exception:
            logger.debug("Failed to close GPT4All embedder", exc_info=True)
        finally:
            self.embedder = None
            self._finalizer = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
