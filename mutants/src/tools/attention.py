"""Attention scoring utilities for tool prioritization."""

from __future__ import annotations

import logging
import math
from typing import Iterable

logger = logging.getLogger(__name__)

# Optional numpy import with graceful fallback
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("NumPy not available, using pure Python fallback")
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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
        else:
            # Pure Python fallback
            d_k = len(query_list)

            # Compute dot products
            scores = []
            for key in keys_list:
                dot_product = sum(q * k for q, k in zip(query_list, key))
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

            weights = [e / sum_exp for e in exp_scores]
            return weights

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
