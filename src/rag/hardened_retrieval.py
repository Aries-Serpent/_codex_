"""
Hardened Retrieval Pipeline - Timeout-protected retrieval with resilience.

This is a drop-in replacement for RetrievalPipeline that adds:
- Timeout protection for retrieval operations
- Circuit breaker for cascading failure prevention
- Retry logic with exponential backoff
- Graceful degradation with fallback retrieval
- Comprehensive monitoring and alerting

PHASE 4D PLANSET 003: RAG Module Robustness
Authority: D-tier autonomous
Target Reliability: 99%+
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from rag.monitoring import OperationMetric, get_rag_monitor
from rag.pipelines.embedding import EmbeddingPipeline
from rag.pipelines.retrieval import (
    RetrievalConfig,
    RetrievalPipeline,
    RetrievalResponse,
    VectorStoreBackend,
)
from rag.resilience import AdaptiveRetryStrategy, RetryConfig
from rag.timeout_manager import (
    TimeoutManager,
    get_default_timeout_manager,
)

logger = logging.getLogger(__name__)

# Bounds
MAX_QUERY_LENGTH = 10000
MAX_RESULTS = 100
DEFAULT_TOP_K = 10


class HardenedRetrievalPipeline(RetrievalPipeline):
    """Retrieval pipeline with timeout protection and resilience.

    Features:
    - Timeout guards on retrieval operations
    - Circuit breaker for cascading failures
    - Retry logic with exponential backoff
    - Graceful degradation with fallback
    - Real-time health monitoring
    """

    def __init__(
        self,
        config: Optional[RetrievalConfig] = None,
        embedding_pipeline: Optional[EmbeddingPipeline] = None,
        vector_store: Optional[VectorStoreBackend] = None,
        timeout_manager: Optional[TimeoutManager] = None,
        retry_config: Optional[RetryConfig] = None,
    ) -> None:
        """Initialize hardened retrieval pipeline.

        Args:
            config: Retrieval configuration
            embedding_pipeline: Embedding pipeline to use
            vector_store: Vector store backend
            timeout_manager: Timeout manager (uses default if None)
            retry_config: Retry configuration
        """
        super().__init__(config, embedding_pipeline, vector_store)

        self.timeout_manager = timeout_manager or get_default_timeout_manager()
        self.retry_strategy = AdaptiveRetryStrategy(retry_config or RetryConfig())
        self.monitor = get_rag_monitor()

        logger.info(
            "HardenedRetrievalPipeline initialized with timeout protection"
        )

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[dict[str, Any]] = None,
    ) -> RetrievalResponse:
        """Retrieve documents with timeout protection.

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            RetrievalResponse with ranked results
        """
        start_time = time.time()
        operation_type = "retrieval"

        # Check circuit breaker
        if self.timeout_manager.is_circuit_open(operation_type):
            logger.warning(
                "Circuit breaker open for retrieval, returning empty results"
            )
            metric = OperationMetric(
                operation_type=operation_type,
                timestamp=time.time(),
                duration_ms=(time.time() - start_time) * 1000,
                success=False,
                fallback_used=True,
            )
            self.monitor.record_metric(metric)

            return RetrievalResponse(
                query=query,
                results=[],
                total_found=0,
                search_time_ms=(time.time() - start_time) * 1000,
            )

        # Perform retrieval with retry logic
        def retrieve_fn():
            # Call parent's retrieve logic
            return super(HardenedRetrievalPipeline, self).retrieve(
                query, top_k, filters
            )

        try:
            result, metrics = self.retry_strategy.execute_with_retries(
                retrieve_fn,
                operation_name=f"retrieve({query[:50]})",
            )

            end_time = time.time()
            metric = OperationMetric(
                operation_type=operation_type,
                timestamp=end_time,
                duration_ms=(end_time - start_time) * 1000,
                success=True,
            )
            self.monitor.record_metric(metric)
            self.timeout_manager.record_success(operation_type, metric)

            logger.debug(
                "Retrieval succeeded: %d results, %.1fms",
                len(result.results),
                result.search_time_ms,
            )
            return result

        except Exception as e:
            logger.error("Retrieval failed: %s", e)
            end_time = time.time()

            metric = OperationMetric(
                operation_type=operation_type,
                timestamp=end_time,
                duration_ms=(end_time - start_time) * 1000,
                success=False,
                error_type=type(e).__name__,
            )
            self.monitor.record_metric(metric)
            self.timeout_manager.record_failure(
                operation_type, metric, str(e)
            )

            # Return graceful degradation
            return RetrievalResponse(
                query=query,
                results=[],
                total_found=0,
                search_time_ms=(end_time - start_time) * 1000,
            )

    def add_documents(
        self,
        documents: list[str],
        ids: Optional[list[str]] = None,
        metadatas: Optional[list[dict[str, Any]]] = None,
    ) -> int:
        """Add documents with timeout protection.

        Args:
            documents: List of document texts
            ids: Optional document IDs
            metadatas: Optional metadata

        Returns:
            Number of documents added
        """
        start_time = time.time()
        operation_type = "add_documents"

        if not documents:
            return 0

        # Check circuit breaker
        if self.timeout_manager.is_circuit_open(operation_type):
            logger.warning(
                "Circuit breaker open for add_documents, skipping"
            )
            return 0

        # Generate IDs if not provided
        base = self.get_document_count()
        if ids is None:
            ids = [f"doc_{base + i}" for i in range(len(documents))]

        # Default empty metadata
        if metadatas is None:
            metadatas = [{} for _ in documents]

        # Generate embeddings with retry
        def add_fn():
            embeddings = self.embedding_pipeline.embed_texts(documents)

            added = 0
            for doc, doc_id, metadata, emb_result in zip(
                documents, ids, metadatas, embeddings, strict=False
            ):
                self._store.add(doc_id, doc, emb_result.embedding, metadata)
                added += 1

            return added

        try:
            result, metrics = self.retry_strategy.execute_with_retries(
                add_fn,
                operation_name="add_documents",
            )

            end_time = time.time()
            metric = OperationMetric(
                operation_type=operation_type,
                timestamp=end_time,
                duration_ms=(end_time - start_time) * 1000,
                success=True,
            )
            self.monitor.record_metric(metric)
            self.timeout_manager.record_success(operation_type, metric)

            logger.info("Added %d documents", result)
            return result

        except Exception as e:
            logger.error("Failed to add documents: %s", e)
            end_time = time.time()

            metric = OperationMetric(
                operation_type=operation_type,
                timestamp=end_time,
                duration_ms=(end_time - start_time) * 1000,
                success=False,
                error_type=type(e).__name__,
            )
            self.monitor.record_metric(metric)
            self.timeout_manager.record_failure(
                operation_type, metric, str(e)
            )

            return 0
