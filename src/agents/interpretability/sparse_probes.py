"""
Sparse Probes for Interpretability

This module implements sparse linear probes for interpreting agent state vectors
into human-understandable concepts and labels.

Core Components:
1. SparseLinearProbe: Maps state vectors to concept scores with L1 sparsity
2. UnembeddingHead: Projects state vectors to label distributions
3. Helper functions: top_k_labels, interpret_state_vector

Physics Inspiration:
- Sparse representations (compressed sensing, signal processing)
- Projection operators (quantum mechanics)
- L1 regularization (LASSO, basis pursuit)
"""

from __future__ import annotations

import logging
import math
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Optional numpy import with graceful fallback
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("NumPy not available, using pure Python fallback")


@dataclass
class SparseLinearProbe:
    """
    Sparse linear probe for concept extraction.

    Maps N-dimensional state vectors to C-dimensional concept scores
    with L1 sparsity regularization.

    Attributes:
        weights: Projection matrix (C x N)
        bias: Bias vector (C,)
        sparsity_threshold: L1 soft-thresholding value
        concept_names: Optional names for concepts
    """

    weights: list[list[float]] = field(default_factory=list)
    bias: list[float] = field(default_factory=list)
    sparsity_threshold: float = 0.1
    concept_names: list[str] = field(default_factory=list)

    @classmethod
    def from_dimensions(
        cls,
        num_concepts: int,
        input_dim: int,
        sparsity_threshold: float = 0.1,
        seed: int = 42,
    ) -> SparseLinearProbe:
        """
        Create probe with deterministic random initialization.

        Args:
            num_concepts: Number of concepts to extract
            input_dim: Dimension of input state vector
            sparsity_threshold: L1 soft-thresholding value
            seed: Random seed for reproducibility

        Returns:
            Initialized probe
        """
        # Use deterministic initialization for testing
        if NUMPY_AVAILABLE:
            rng = np.random.RandomState(seed)
            weights = rng.randn(num_concepts, input_dim) * 0.1
            bias = rng.randn(num_concepts) * 0.01
            weights_list = weights.tolist()
            bias_list = bias.tolist()
        else:
            # Pure Python fallback
            import random

            random.seed(seed)
            weights_list = [
                [random.gauss(0, 0.1) for _ in range(input_dim)]
                for _ in range(num_concepts)
            ]
            bias_list = [random.gauss(0, 0.01) for _ in range(num_concepts)]

        concept_names = [f"concept_{i}" for i in range(num_concepts)]

        return cls(
            weights=weights_list,
            bias=bias_list,
            sparsity_threshold=sparsity_threshold,
            concept_names=concept_names,
        )

    def transform(self, vector: Iterable[float]) -> list[float]:
        """
        Transform state vector to concept scores.

        Applies: concepts = W @ vector + b
        Then applies L1 soft-thresholding for sparsity.

        Args:
            vector: Input state vector (N,)

        Returns:
            Concept scores (C,)
        """
        vector_list = list(vector)

        if NUMPY_AVAILABLE:
            vec_array = np.array(vector_list)
            weights_array = np.array(self.weights)
            bias_array = np.array(self.bias)

            # Linear projection
            concepts = weights_array @ vec_array + bias_array

            # L1 soft-thresholding (sparsity)
            concepts = np.sign(concepts) * np.maximum(
                np.abs(concepts) - self.sparsity_threshold, 0
            )

            return concepts.tolist()
        # Pure Python fallback
        concepts = []
        for i, weight_row in enumerate(self.weights):
            # Dot product
            score = sum(w * v for w, v in zip(weight_row, vector_list))
            score += self.bias[i]

            # L1 soft-thresholding
            if abs(score) > self.sparsity_threshold:
                score = math.copysign(
                    abs(score) - self.sparsity_threshold, score
                )
            else:
                score = 0.0

            concepts.append(score)

        return concepts

    def top_concepts(self, vector: Iterable[float], k: int = 3) -> list[tuple[str, float]]:
        """
        Get top-k concepts for a state vector.

        Args:
            vector: Input state vector
            k: Number of top concepts to return

        Returns:
            List of (concept_name, score) tuples
        """
        concepts = self.transform(vector)

        # Create (name, score) pairs
        named_concepts = list(zip(self.concept_names, concepts))

        # Sort by absolute score (most active concepts)
        named_concepts.sort(key=lambda x: abs(x[1]), reverse=True)

        return named_concepts[:k]

    def sparsity_ratio(self) -> float:
        """
        Calculate sparsity ratio of weight matrix.

        Returns:
            Fraction of weights that are effectively zero
        """
        total_weights = 0
        zero_weights = 0

        for row in self.weights:
            for w in row:
                total_weights += 1
                if abs(w) < 1e-6:
                    zero_weights += 1

        return zero_weights / total_weights if total_weights > 0 else 0.0


@dataclass
class UnembeddingHead:
    """
    Unembedding head for label projection.

    Maps N-dimensional state vectors to V-dimensional label logits.

    Attributes:
        weights: Projection matrix (V x N)
        bias: Bias vector (V,)
        label_names: Optional names for labels
    """

    weights: list[list[float]] = field(default_factory=list)
    bias: list[float] = field(default_factory=list)
    label_names: list[str] = field(default_factory=list)

    @classmethod
    def from_dimensions(
        cls,
        num_labels: int,
        input_dim: int,
        seed: int = 42,
    ) -> UnembeddingHead:
        """
        Create unembedding head with deterministic initialization.

        Args:
            num_labels: Number of labels in vocabulary
            input_dim: Dimension of input state vector
            seed: Random seed for reproducibility

        Returns:
            Initialized unembedding head
        """
        if NUMPY_AVAILABLE:
            rng = np.random.RandomState(seed)
            weights = rng.randn(num_labels, input_dim) * 0.1
            bias = rng.randn(num_labels) * 0.01
            weights_list = weights.tolist()
            bias_list = bias.tolist()
        else:
            # Pure Python fallback
            import random

            random.seed(seed)
            weights_list = [
                [random.gauss(0, 0.1) for _ in range(input_dim)]
                for _ in range(num_labels)
            ]
            bias_list = [random.gauss(0, 0.01) for _ in range(num_labels)]

        label_names = [f"label_{i}" for i in range(num_labels)]

        return cls(
            weights=weights_list,
            bias=bias_list,
            label_names=label_names,
        )

    def project(self, vector: Iterable[float]) -> list[float]:
        """
        Project state vector to label logits.

        Applies: logits = W @ vector + b

        Args:
            vector: Input state vector (N,)

        Returns:
            Label logits (V,)
        """
        vector_list = list(vector)

        if NUMPY_AVAILABLE:
            vec_array = np.array(vector_list)
            weights_array = np.array(self.weights)
            bias_array = np.array(self.bias)

            logits = weights_array @ vec_array + bias_array
            return logits.tolist()
        # Pure Python fallback
        logits = []
        for i, weight_row in enumerate(self.weights):
            # Dot product
            score = sum(w * v for w, v in zip(weight_row, vector_list))
            score += self.bias[i]
            logits.append(score)

        return logits


def top_k_labels(
    logits: Iterable[float],
    label_names: list[str],
    k: int = 3,
) -> list[tuple[str, float]]:
    """
    Get top-k labels from logits.

    Args:
        logits: Label logits (V,)
        label_names: Names for each label
        k: Number of top labels to return

    Returns:
        List of (label_name, logit_score) tuples sorted by score
    """
    logits_list = list(logits)

    # Create (name, logit) pairs
    named_logits = list(zip(label_names, logits_list))

    # Sort by logit score (highest first)
    named_logits.sort(key=lambda x: x[1], reverse=True)

    return named_logits[:k]


def interpret_state_vector(
    vector: Iterable[float],
    *,
    probe: Optional[SparseLinearProbe] = None,
    unembedding: Optional[UnembeddingHead] = None,
    top_k: int = 3,
) -> dict[str, Any]:
    """
    Interpret state vector into concepts and labels.

    Orchestrator function that combines sparse probe and unembedding head
    to provide a comprehensive interpretation of an agent state vector.

    Args:
        vector: Input state vector
        probe: Optional sparse probe for concept extraction
        unembedding: Optional unembedding head for label projection
        top_k: Number of top concepts/labels to return

    Returns:
        Dictionary with:
            - concepts: List of (concept_name, score) tuples
            - labels: List of (label_name, logit) tuples
            - confidence: Overall confidence score
    """
    result: dict[str, Any] = {
        "concepts": [],
        "labels": [],
        "confidence": 0.0,
    }

    # Extract concepts if probe provided
    if probe is not None:
        try:
            concepts = probe.top_concepts(vector, k=top_k)
            result["concepts"] = concepts

            # Calculate confidence from concept magnitudes
            if concepts:
                result["confidence"] = sum(abs(score) for _, score in concepts) / len(
                    concepts
                )
        except Exception as e:
            logger.error(f"Failed to extract concepts: {e}")

    # Project to labels if unembedding provided
    if unembedding is not None:
        try:
            logits = unembedding.project(vector)
            labels = top_k_labels(logits, unembedding.label_names, k=top_k)
            result["labels"] = labels

            # Update confidence with label logits if concepts not available
            if result["confidence"] == 0.0 and labels:
                # Use softmax-like normalization
                max_logit = max(logit for _, logit in labels)
                result["confidence"] = 1.0 / (1.0 + math.exp(-max_logit))
        except Exception as e:
            logger.error(f"Failed to project labels: {e}")

    return result
