"""
llama.cpp Embedding Provider

Provides embeddings using llama.cpp inference engine.
"""

import logging
from typing import Optional, Union

import numpy as np

logger = logging.getLogger(__name__)


def _finalize_model(model: object | None) -> None:
    """Best-effort cleanup for llama.cpp model resources."""
    if model is None:
        return
    try:
        close = getattr(model, "close", None)
        if callable(close):
            close()
    except Exception:
        logger.debug("Failed to finalize llama.cpp model", exc_info=True)

try:
    from llama_cpp import Llama

    LLAMACPP_AVAILABLE = True
except ImportError:
    LLAMACPP_AVAILABLE = False
    logger.debug("llama-cpp-python not installed")


class LlamaCppEmbeddingProvider:
    """
    Embedding provider using llama.cpp inference engine.

    llama.cpp is a highly optimized C/C++ inference engine for LLaMA-family
    models. This provider loads GGUF quantized models for embedding generation.

    Supported formats:
    - GGUF quantized models (Q4_K_M, Q5_K_M, Q8_0, etc.)
    - Any llama.cpp compatible embedding model

    Example:
        >>> provider = LlamaCppEmbeddingProvider(
        ...     model_path='/models/nomic-embed-q4.gguf',
        ...     n_gpu_layers=32
        ... )
        >>> embeddings = provider.encode(['Hello world', 'Test document'])
        >>> logger.info(embeddings.shape)
        (2, 768)
    """

    def __init__(
        self,
        model_path: str,
        n_ctx: int = 512,
        n_gpu_layers: int = 0,
        n_threads: Optional[int] = None,
        embedding: bool = True,
        dimension: int = 768,
    ):
        """
        Initialize llama.cpp embedding provider.

        Args:
            model_path: Path to GGUF model file
            n_ctx: Context window size
            n_gpu_layers: Number of layers to offload to GPU (0 = CPU only)
            n_threads: Number of threads (None = auto-detect)
            embedding: Enable embedding mode
            dimension: Expected embedding dimension
        """
        if not LLAMACPP_AVAILABLE:
            raise ImportError(
                "llama-cpp-python not installed. Install with: pip install llama-cpp-python"
            )

        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.n_threads = n_threads
        self.dimension = dimension

        try:
            self.model = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                n_threads=n_threads,
                embedding=embedding,
                verbose=False,
            )
            logger.info(f"Loaded llama.cpp model from {model_path}")

            # Auto-detect dimension
            test_embedding = self.model.create_embedding("test")
            if isinstance(test_embedding, dict) and "data" in test_embedding:
                detected_dim = len(test_embedding["data"][0]["embedding"])
                self.dimension = detected_dim
                logger.debug(f"Detected embedding dimension: {detected_dim}")

        except (ValueError, TypeError) as e:
            type(e).__name__
            logger.error("Failed to load llama.cpp model: <ERROR_TYPE>")
            raise

    def encode(
        self,
        texts: Union[str, list[str]],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> np.ndarray:
        """
        Generate embeddings for texts using llama.cpp.

        Args:
            texts: Single text or list of texts to embed
            batch_size: Batch size (llama.cpp processes one at a time)
            show_progress: Show progress bar (not implemented)

        Returns:
            numpy array of embeddings with shape (n, dimension)
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = []
        for text in texts:
            try:
                result = self.model.create_embedding(text)

                if isinstance(result, dict) and "data" in result:
                    embedding = result["data"][0]["embedding"]
                    embeddings.append(embedding)
                else:
                    logger.error(f"Unexpected embedding format: {type(result)}")
                    embeddings.append([0.0] * self.dimension)

            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.error("Error encoding text: <ERROR_TYPE>")
                embeddings.append([0.0] * self.dimension)

        return np.array(embeddings, dtype=np.float32)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension

    def __repr__(self) -> str:
        return f"LlamaCppEmbeddingProvider(model={self.model_path}, gpu_layers={self.n_gpu_layers})"

    def close(self) -> None:
        """Close the optional model resource without relying on __del__."""
        model = getattr(self, "model", None)
        try:
            if model is not None:
                close = getattr(model, "close", None)
                if callable(close):
                    close()
        except Exception:
            logger.debug("Failed to close llama.cpp model", exc_info=True)
        finally:
            self.model = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
