"""
Result Re-ranking Module for RAG Pipeline

Provides production-grade re-ranking capabilities:
- Cross-encoder based re-ranking
- Score fusion from multiple sources
- Diversity-aware re-ranking
- Configurable ranking strategies
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class RerankingStrategy(Enum):
    """Available re-ranking strategies."""

    NONE = "none"  # No re-ranking
    SCORE_FUSION = "score_fusion"  # Combine scores from multiple sources
    CROSS_ENCODER = "cross_encoder"  # Neural cross-encoder
    MMR = "mmr"  # Maximal Marginal Relevance (diversity)
    HYBRID = "hybrid"  # Combine multiple strategies


@dataclass
class RerankingConfig:
    """Configuration for re-ranking."""

    strategy: RerankingStrategy = RerankingStrategy.SCORE_FUSION

    # Score fusion parameters
    fusion_weights: dict[str, float] = field(
        default_factory=lambda: {"semantic": 0.7, "lexical": 0.3}
    )
    fusion_method: str = "weighted_sum"  # weighted_sum, reciprocal_rank, max

    # MMR parameters (diversity)
    mmr_lambda: float = 0.5  # Balance relevance vs diversity (0-1)

    # Cross-encoder parameters
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    cross_encoder_batch_size: int = 32

    # General parameters
    top_k: int = 10  # Number of results to return after re-ranking
    score_threshold: float = 0.0  # Minimum score threshold


@dataclass
class RankedResult:
    """A single ranked result."""

    document_id: str
    content: str
    original_score: float
    reranked_score: float
    rank: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "content": self.content,
            "original_score": self.original_score,
            "reranked_score": self.reranked_score,
            "rank": self.rank,
            "metadata": self.metadata,
        }


class BaseReranker(ABC):
    """Base class for re-ranking strategies."""

    def __init__(self, config: RerankingConfig):
        self.config = config

    @abstractmethod
    def rerank(
        self,
        query: str,
        results: Sequence[dict[str, Any]],
    ) -> list[RankedResult]:
        """Re-rank results based on query."""


class ScoreFusionReranker(BaseReranker):
    """
    Score fusion re-ranker.

    Combines scores from multiple retrieval sources using
    configurable fusion methods.
    """

    def rerank(
        self,
        query: str,
        results: Sequence[dict[str, Any]],
    ) -> list[RankedResult]:
        """Re-rank using score fusion."""
        if not results:
            return []

        ranked_results = []

        for idx, result in enumerate(results):
            # Extract scores from different sources
            scores = {}
            for source, weight in self.config.fusion_weights.items():
                score_key = f"{source}_score"
                if score_key in result:
                    scores[source] = result[score_key] * weight
                elif "score" in result:
                    # Use single score if source-specific not available
                    scores[source] = result["score"] * weight

            # Compute fused score
            if self.config.fusion_method == "weighted_sum":
                fused_score = sum(scores.values())
            elif self.config.fusion_method == "reciprocal_rank":
                # Reciprocal rank fusion using document position
                # Position (idx) is used as the rank; lower idx = better rank
                doc_rank = idx + 1  # 1-indexed rank
                fused_score = 1.0 / (60 + doc_rank)
            elif self.config.fusion_method == "max":
                fused_score = max(scores.values()) if scores else 0.0
            else:
                fused_score = sum(scores.values())

            ranked_result = RankedResult(
                document_id=result.get("id", result.get("document_id", "")),
                content=result.get("content", result.get("text", "")),
                original_score=result.get("score", 0.0),
                reranked_score=fused_score,
                rank=0,  # Will be set after sorting
                metadata=result.get("metadata", {}),
            )
            ranked_results.append(ranked_result)

        # Sort by fused score (descending)
        ranked_results.sort(key=lambda x: x.reranked_score, reverse=True)

        # Apply threshold and top_k
        ranked_results = [
            r for r in ranked_results if r.reranked_score >= self.config.score_threshold
        ][: self.config.top_k]

        # Set final ranks
        for i, result in enumerate(ranked_results):  # type: ignore[assignment]
            result.rank = i + 1  # type: ignore[attr-defined]

        logger.debug(f"Score fusion re-ranked {len(ranked_results)} results")
        return ranked_results


class MMRReranker(BaseReranker):
    """
    Maximal Marginal Relevance (MMR) re-ranker.

    Balances relevance with diversity to avoid redundant results.
    Uses the formula: MMR = λ * sim(q, d) - (1-λ) * max_s∈S sim(d, s)
    """

    def rerank(
        self,
        query: str,
        results: Sequence[dict[str, Any]],
        embeddings: Optional[np.ndarray] = None,
    ) -> list[RankedResult]:
        """Re-rank using MMR for diversity."""
        if not results:
            return []

        n_results = len(results)

        # Extract relevance scores
        relevance_scores = np.array([r.get("score", 0.0) for r in results])

        # If embeddings provided, compute diversity matrix
        if embeddings is not None and len(embeddings) == n_results:
            # Cosine similarity matrix
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms = np.clip(norms, 1e-10, None)  # Avoid division by zero
            normalized = embeddings / norms
            similarity_matrix = np.dot(normalized, normalized.T)
        else:
            # No embeddings, use identity (no diversity penalty)
            similarity_matrix = np.eye(n_results)

        # MMR selection
        selected_indices: list[Any] = []
        remaining_indices = list(range(n_results))

        lambda_param = self.config.mmr_lambda

        while remaining_indices and len(selected_indices) < self.config.top_k:
            if not selected_indices:
                # First selection: highest relevance
                best_idx = np.argmax(relevance_scores[remaining_indices])
                best_idx = remaining_indices[best_idx]
            else:
                # MMR selection
                best_score = float("-inf")
                best_idx = remaining_indices[0]

                for idx in remaining_indices:
                    relevance = relevance_scores[idx]

                    # Max similarity to already selected
                    max_sim = max(similarity_matrix[idx, sel_idx] for sel_idx in selected_indices)

                    # MMR score
                    mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim

                    if mmr_score > best_score:
                        best_score = mmr_score
                        best_idx = idx

            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)

        # Build ranked results
        ranked_results = []
        for rank, idx in enumerate(selected_indices, 1):
            result = results[idx]
            ranked_result = RankedResult(
                document_id=result.get("id", result.get("document_id", "")),
                content=result.get("content", result.get("text", "")),
                original_score=result.get("score", 0.0),
                reranked_score=relevance_scores[idx],
                rank=rank,
                metadata=result.get("metadata", {}),
            )
            ranked_results.append(ranked_result)

        logger.debug(f"MMR re-ranked {len(ranked_results)} results (λ={lambda_param})")
        return ranked_results


class CrossEncoderReranker(BaseReranker):
    """
    Cross-encoder based re-ranker.

    Uses a neural cross-encoder model to score query-document pairs.
    More accurate but slower than bi-encoder approaches.
    """

    def __init__(self, config: RerankingConfig):
        super().__init__(config)
        self._model = None
        self._model_loaded = False

    def _load_model(self) -> Any:
        """Lazy load cross-encoder model."""
        if self._model_loaded:
            return self._model

        try:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self.config.cross_encoder_model)
            self._model_loaded = True
            logger.info(f"Loaded cross-encoder: {self.config.cross_encoder_model}")
            return self._model
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            self._model_loaded = True
            return None

    def rerank(
        self,
        query: str,
        results: Sequence[dict[str, Any]],
    ) -> list[RankedResult]:
        """Re-rank using cross-encoder."""
        if not results:
            return []

        model = self._load_model()

        # Extract documents
        documents = [r.get("content", r.get("text", "")) for r in results]

        # Score with cross-encoder
        if model is not None:
            # Create query-document pairs
            pairs = [(query, doc) for doc in documents]

            # Batch scoring
            scores = model.predict(
                pairs,
                batch_size=self.config.cross_encoder_batch_size,
            )
        else:
            # Fallback to original scores if model unavailable
            scores = [r.get("score", 0.0) for r in results]

        # Build ranked results
        ranked_results = []
        for i, (result, score) in enumerate(zip(results, scores, strict=False)):
            ranked_result = RankedResult(
                document_id=result.get("id", result.get("document_id", "")),
                content=documents[i],
                original_score=result.get("score", 0.0),
                reranked_score=float(score),
                rank=0,
                metadata=result.get("metadata", {}),
            )
            ranked_results.append(ranked_result)

        # Sort by cross-encoder score (descending)
        ranked_results.sort(key=lambda x: x.reranked_score, reverse=True)

        # Apply threshold and top_k
        ranked_results = [
            r for r in ranked_results if r.reranked_score >= self.config.score_threshold
        ][: self.config.top_k]

        # Set final ranks
        for i, result in enumerate(ranked_results):  # type: ignore[assignment]
            result.rank = i + 1  # type: ignore[attr-defined]

        logger.debug(f"Cross-encoder re-ranked {len(ranked_results)} results")
        return ranked_results


class Reranker:
    """
    Main re-ranker class that dispatches to appropriate strategy.

    Example:
        config = RerankingConfig(
            strategy=RerankingStrategy.MMR,
            mmr_lambda=0.7,
            top_k=10,
        )
        reranker = Reranker(config)

        results = retriever.search(query)
        reranked = reranker.rerank(query, results)
    """

    STRATEGY_MAP = {
        RerankingStrategy.SCORE_FUSION: ScoreFusionReranker,
        RerankingStrategy.MMR: MMRReranker,
        RerankingStrategy.CROSS_ENCODER: CrossEncoderReranker,
    }

    def __init__(self, config: Optional[RerankingConfig] = None):
        """Initialize re-ranker with configuration."""
        self.config = config or RerankingConfig()

        if self.config.strategy == RerankingStrategy.NONE:
            self._reranker = None
        elif self.config.strategy == RerankingStrategy.HYBRID:
            # Hybrid combines multiple strategies
            self._rerankers = {
                "mmr": MMRReranker(self.config),
                "fusion": ScoreFusionReranker(self.config),
            }
            self._reranker = None
        else:
            reranker_class = self.STRATEGY_MAP.get(self.config.strategy, ScoreFusionReranker)
            self._reranker = reranker_class(self.config)  # type: ignore[abstract]

    def rerank(
        self,
        query: str,
        results: Sequence[dict[str, Any]],
        embeddings: Optional[np.ndarray] = None,
    ) -> list[RankedResult]:
        """
        Re-rank search results.

        Args:
            query: Original search query
            results: List of search results to re-rank
            embeddings: Optional embeddings for diversity-aware re-ranking

        Returns:
            List of RankedResult objects
        """
        if not results:
            return []

        if self.config.strategy == RerankingStrategy.NONE:
            # No re-ranking, just wrap results
            return self._wrap_results(results)

        if self.config.strategy == RerankingStrategy.HYBRID:
            return self._hybrid_rerank(query, results, embeddings)

        if self.config.strategy == RerankingStrategy.MMR:
            return self._reranker.rerank(query, results, embeddings)  # type: ignore[union-attr,call-arg]

        return self._reranker.rerank(query, results)  # type: ignore[union-attr]

    def _wrap_results(self, results: Sequence[dict[str, Any]]) -> list[RankedResult]:
        """Wrap raw results as RankedResult without re-ranking."""
        wrapped = []
        for i, result in enumerate(results[: self.config.top_k], 1):
            wrapped.append(
                RankedResult(
                    document_id=result.get("id", result.get("document_id", "")),
                    content=result.get("content", result.get("text", "")),
                    original_score=result.get("score", 0.0),
                    reranked_score=result.get("score", 0.0),
                    rank=i,
                    metadata=result.get("metadata", {}),
                )
            )
        return wrapped

    def _hybrid_rerank(
        self,
        query: str,
        results: Sequence[dict[str, Any]],
        embeddings: Optional[np.ndarray] = None,
    ) -> list[RankedResult]:
        """Apply hybrid re-ranking strategy."""
        # First apply score fusion
        fusion_results = self._rerankers["fusion"].rerank(query, results)

        # Convert back to dict format for MMR
        intermediate_results = [
            {
                "id": r.document_id,
                "content": r.content,
                "score": r.reranked_score,
                "metadata": r.metadata,
            }
            for r in fusion_results
        ]

        # Then apply MMR for diversity
        final_results = self._rerankers["mmr"].rerank(query, intermediate_results, embeddings)  # type: ignore[call-arg]

        logger.debug(f"Hybrid re-ranked {len(final_results)} results")
        return final_results


def rerank_results(
    query: str,
    results: Sequence[dict[str, Any]],
    strategy: RerankingStrategy = RerankingStrategy.SCORE_FUSION,
    top_k: int = 10,
    **kwargs: Any,
) -> list[RankedResult]:
    """
    Convenience function to re-rank results.

    Args:
        query: Search query
        results: Results to re-rank
        strategy: Re-ranking strategy
        top_k: Number of results to return
        **kwargs: Additional config options

    Returns:
        List of RankedResult objects
    """
    config = RerankingConfig(
        strategy=strategy,
        top_k=top_k,
        **kwargs,
    )
    reranker = Reranker(config)
    return reranker.rerank(query, results)
