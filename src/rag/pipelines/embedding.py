"""
Embedding Pipeline - Generate vector embeddings for text.

This module provides embedding functionality for the RAG pipeline.
Uses lazy imports to avoid requiring heavy ML dependencies when not used.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Lazy import of embedding dependencies
- Bounds checking on text length
- Fallback to simple hash-based embeddings
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MAX_TEXT_LENGTH = 100000
DEFAULT_EMBEDDING_DIM = 384


@dataclass
class EmbeddingConfig:
    """Configuration for the embedding pipeline."""

    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = DEFAULT_EMBEDDING_DIM
    normalize: bool = True
    batch_size: int = 32


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""

    text: str
    embedding: list[float]
    model: str
    dimension: int


class EmbeddingPipeline:
    """
    Pipeline for generating text embeddings.

    Features:
    - Support for sentence-transformers models
    - Fallback to hash-based embeddings for testing
    - Batch processing for efficiency

    Safeguards:
    - Lazy loading of ML dependencies
    - Text length validation
    - Graceful fallback on errors
    """

    def __init__(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model: Any = None
        self._use_fallback = False

        logger.info(
            "EmbeddingPipeline initialized: model=%s, dim=%d",
            self.config.model_name,
            self.config.dimension,
        )

    def _load_model(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except (OSError, ValueError, TypeError, RuntimeError) as e:
            logger.warning(
                "Failed to load embedding model '%s'; using fallback embeddings: %s",
                self.config.model_name,
                e,
            )
            self._use_fallback = True
            return False

    def _fallback_embedding(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i : i + 2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[: self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def embed_text(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(text, normalize_embeddings=normalize)
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except (OSError, ValueError, TypeError, RuntimeError) as e:
                text_fingerprint = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
                logger.warning(
                    "Embedding failed for text fingerprint '%s' with model '%s'; using fallback (%s)",
                    text_fingerprint,
                    self.config.model_name,
                    type(e).__name__,
                )
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def embed_texts(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings, strict=False):
                    results.append(
                        EmbeddingResult(
                            text=text[:100],
                            embedding=embedding.tolist(),
                            model=self.config.model_name,
                            dimension=len(embedding),
                        )
                    )

            except (OSError, ValueError, TypeError, RuntimeError) as e:
                logger.warning(
                    "Batch embedding failed for model '%s'; using fallback: %s",
                    self.config.model_name,
                    e,
                )
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def get_dimension(self) -> int:
        """Return the embedding dimension."""
        return self.config.dimension


def main() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    logger.info(f"Single embedding: dim={result.dimension}, model={result.model}")
    logger.info(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    logger.info(f"\nBatch embedding: {len(results)} results")
    for r in results:
       logger.info(f"  - {r.text}: dim={r.dimension}")


if __name__ == "__main__":
    main()
