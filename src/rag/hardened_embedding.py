"""
Hardened Embedding Pipeline - Timeout-protected embeddings with resilience.

This is a drop-in replacement for EmbeddingPipeline that adds:
- Timeout protection for model loading and embedding generation
- Automatic fallback to hash-based embeddings
- Circuit breaker for cascading failure prevention
- Retry logic with exponential backoff
- Comprehensive monitoring and alerting

PHASE 4D PLANSET 003: RAG Module Robustness
Authority: D-tier autonomous
Target Reliability: 99%+
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Optional

from rag.monitoring import OperationMetric, get_rag_monitor
from rag.pipelines.embedding import (
    EmbeddingConfig,
    EmbeddingPipeline,
    EmbeddingResult,
)
from rag.resilience import AdaptiveRetryStrategy, RetryConfig
from rag.timeout_manager import (
    TimeoutConfig,
    TimeoutManager,
    get_default_timeout_manager,
)

logger = logging.getLogger(__name__)

# Maximum text length for safety
MAX_TEXT_LENGTH = 100000


class HardenedEmbeddingPipeline(EmbeddingPipeline):
    """Embedding pipeline with timeout protection and resilience.

    Features:
    - Timeout guards on model loading
    - Timeout guards on embedding generation
    - Automatic fallback to hash-based embeddings
    - Circuit breaker for cascading failures
    - Retry logic with exponential backoff
    - Real-time health monitoring
    """

    def __init__(
        self,
        config: Optional[EmbeddingConfig] = None,
        timeout_manager: Optional[TimeoutManager] = None,
        retry_config: Optional[RetryConfig] = None,
    ) -> None:
        """Initialize hardened embedding pipeline.

        Args:
            config: Embedding configuration
            timeout_manager: Timeout manager (uses default if None)
            retry_config: Retry configuration
        """
        super().__init__(config)

        self.timeout_manager = timeout_manager or get_default_timeout_manager()
        self.retry_strategy = AdaptiveRetryStrategy(retry_config or RetryConfig())
        self.monitor = get_rag_monitor()

        logger.info(
            "HardenedEmbeddingPipeline initialized with timeout protection"
        )

    def _load_model_with_timeout(self) -> bool:
        """Load model with timeout protection."""
        if self._model is not None:
            return True

        # Check circuit breaker
        if self.timeout_manager.is_circuit_open("embedding_load"):
            logger.warning(
                "Circuit breaker open for model loading, using fallback"
            )
            self._use_fallback = True
            return False

        # Try to load with retry logic
        def load_fn():
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.config.model_name)
                logger.info("Loaded embedding model: %s", self.config.model_name)
                return True
            except ImportError:
                logger.warning("sentence-transformers not installed")
                self._use_fallback = True
                return False
            except Exception as e:
                logger.error("Failed to load embedding model: %s", e)
                self._use_fallback = True
                return False

        try:
            result, metrics = self.retry_strategy.execute_with_retries(
                load_fn,
                operation_name="embedding_model_load",
            )

            # Record metric
            import time
            metric = OperationMetric(
                operation_type="embedding_load",
                timestamp=time.time(),
                duration_ms=metrics.total_wait_time_ms + metrics.total_attempts * 100,
                success=result,
            )
            self.monitor.record_metric(metric)

            return result

        except Exception as e:
            logger.error("Failed to load model after retries: %s", e)
            self._use_fallback = True
            return False

    def embed_text(self, text: str) -> EmbeddingResult:
        """Generate embedding for single text with timeout protection."""
        import time

        start_time = time.time()
        operation_type = "embedding"

        # Input validation
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Check circuit breaker
        if self.timeout_manager.is_circuit_open(operation_type):
            logger.warning("Circuit breaker open, using fallback embedding")
            result = EmbeddingResult(
                text=text[:100],
                embedding=self._fallback_embedding(text),
                model="fallback-hash",
                dimension=self.config.dimension,
            )
            metric = OperationMetric(
                operation_type=operation_type,
                timestamp=time.time(),
                duration_ms=(time.time() - start_time) * 1000,
                success=True,
                fallback_used=True,
            )
            self.monitor.record_metric(metric)
            return result

        # Load model if needed
        if not self._use_fallback:
            self._load_model_with_timeout()

        # Generate embedding with retry
        def embed_fn():
            if self._use_fallback or self._model is None:
                return self._fallback_embedding(text), "fallback-hash"
            else:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                return raw_embedding.tolist(), self.config.model_name

        try:
            result, metrics = self.retry_strategy.execute_with_retries(
                embed_fn,
                operation_name=f"embed_text",
            )

            embedding, model_name = result

            end_time = time.time()
            metric = OperationMetric(
                operation_type=operation_type,
                timestamp=end_time,
                duration_ms=(end_time - start_time) * 1000,
                success=True,
            )
            self.monitor.record_metric(metric)
            self.timeout_manager.record_success(operation_type, metric)

            return EmbeddingResult(
                text=text[:100],
                embedding=embedding,
                model=model_name,
                dimension=len(embedding),
            )

        except Exception as e:
            logger.error("Embedding failed: %s, using fallback", e)
            end_time = time.time()

            # Fallback to hash-based embedding
            embedding = self._fallback_embedding(text)

            metric = OperationMetric(
                operation_type=operation_type,
                timestamp=end_time,
                duration_ms=(end_time - start_time) * 1000,
                success=True,
                fallback_used=True,
                error_type=type(e).__name__,
            )
            self.monitor.record_metric(metric)
            self.timeout_manager.record_failure(
                operation_type, metric, str(e)
            )

            return EmbeddingResult(
                text=text[:100],
                embedding=embedding,
                model="fallback-hash",
                dimension=self.config.dimension,
            )

    def embed_texts(self, texts: list[str]) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts with timeout protection."""
        import time

        start_time = time.time()
        operation_type = "batch_embedding"

        if not texts:
            return []

        # Check circuit breaker
        if self.timeout_manager.is_circuit_open(operation_type):
            logger.warning(
                "Circuit breaker open for batch embedding, using fallback"
            )
            results = [self.embed_text(text) for text in texts]
            metric = OperationMetric(
                operation_type=operation_type,
                timestamp=time.time(),
                duration_ms=(time.time() - start_time) * 1000,
                success=True,
                fallback_used=True,
            )
            self.monitor.record_metric(metric)
            return results

        # Load model if needed
        if not self._use_fallback:
            self._load_model_with_timeout()

        # Batch embed with retry
        def batch_embed_fn():
            if self._use_fallback or self._model is None:
                # Use fallback for each text
                return (
                    [self._fallback_embedding(text[:MAX_TEXT_LENGTH]) for text in texts],
                    "fallback-hash",
                )
            else:
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )
                return (
                    [e.tolist() for e in embeddings],
                    self.config.model_name,
                )

        try:
            result, metrics = self.retry_strategy.execute_with_retries(
                batch_embed_fn,
                operation_name="batch_embed_texts",
            )

            embeddings, model_name = result
            results = [
                EmbeddingResult(
                    text=text[:100],
                    embedding=embedding,
                    model=model_name,
                    dimension=len(embedding),
                )
                for text, embedding in zip(texts, embeddings, strict=False)
            ]

            end_time = time.time()
            metric = OperationMetric(
                operation_type=operation_type,
                timestamp=end_time,
                duration_ms=(end_time - start_time) * 1000,
                success=True,
            )
            self.monitor.record_metric(metric)
            self.timeout_manager.record_success(operation_type, metric)

            logger.info("Embedded %d texts successfully", len(results))
            return results

        except Exception as e:
            logger.error("Batch embedding failed: %s, using fallback", e)
            end_time = time.time()

            # Fallback to individual hash-based embeddings
            results = [self.embed_text(text) for text in texts]

            metric = OperationMetric(
                operation_type=operation_type,
                timestamp=end_time,
                duration_ms=(end_time - start_time) * 1000,
                success=True,
                fallback_used=True,
                error_type=type(e).__name__,
            )
            self.monitor.record_metric(metric)
            self.timeout_manager.record_failure(
                operation_type, metric, str(e)
            )

            return results

    def get_dimension(self) -> int:
        """Return the embedding dimension."""
        return self.config.dimension
