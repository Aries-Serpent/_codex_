"""Attention scoring utilities for tool prioritization."""

from __future__ import annotations

import logging
import math
from collections.abc import Iterable

logger = logging.getLogger(__name__)

# Optional numpy import with graceful fallback
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("NumPy not available, using pure Python fallback")


class AttentionScorer:
    """
    Compute attention weights for query/key vectors.

    Implements scaled dot-product attention from Transformer architecture:
        attention(Q, K) = softmax(Q·K^T / sqrt(d_k))

    This allows tools to be prioritized based on semantic similarity
    between the task (query) and tool embeddings (keys).
    """

    @staticmethod
    def score(
        query_vec: Iterable[float],
        key_matrix: Iterable[Iterable[float]],
        *,
        temperature: float = 1.0,
    ) -> list[float]:
        """
        Compute softmax attention weights.

        Args:
            query_vec: Query vector (task embedding)
            key_matrix: Key matrix (tool embeddings), shape (N, d)
            temperature: Temperature for softmax (higher = more uniform)

        Returns:
            Attention weights (N,), summing to 1.0
        """
        query_list = list(query_vec)
        keys_list = [list(key) for key in key_matrix]

        if len(keys_list) == 0:
            return []

        # Compute dot products
        if NUMPY_AVAILABLE:
            q = np.array(query_list)
            K = np.array(keys_list)

            # Scaled dot-product attention
            d_k = len(query_list)
            scores = K @ q / math.sqrt(d_k)

            # Apply temperature
            scores = scores / temperature

            # Softmax
            exp_scores = np.exp(scores - np.max(scores))  # Numerical stability
            weights = exp_scores / np.sum(exp_scores)

            return weights.tolist()
        # Pure Python fallback
        d_k = len(query_list)

        # Compute dot products
        scores = []
        for key in keys_list:
            dot_product = sum(q * k for q, k in zip(query_list, key, strict=False))
            scores.append(dot_product / math.sqrt(d_k))

        # Apply temperature
        scores = [s / temperature for s in scores]

        # Softmax with numerical stability
        max_score = max(scores) if scores else 0.0
        exp_scores = [math.exp(s - max_score) for s in scores]
        sum_exp = sum(exp_scores)

        if sum_exp == 0:
            # Uniform distribution if all scores are -inf
            return [1.0 / len(keys_list)] * len(keys_list)

        return [e / sum_exp for e in exp_scores]

    @staticmethod
    def top_k_indices(
        weights: Iterable[float],
        k: int = 3,
    ) -> list[int]:
        """
        Get indices of top-k attention weights.

        Args:
            weights: Attention weights
            k: Number of top items to return

        Returns:
            List of indices sorted by weight (descending)
        """
        weights_list = list(weights)

        # Create (index, weight) pairs
        indexed_weights = list(enumerate(weights_list))

        # Sort by weight (descending)
        indexed_weights.sort(key=lambda x: x[1], reverse=True)

        # Return top-k indices
        return [idx for idx, _ in indexed_weights[:k]]
