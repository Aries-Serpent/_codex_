"""Lightweight MLP scoring for action paths."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Iterable

logger = logging.getLogger(__name__)

# Optional numpy import with graceful fallback
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("NumPy not available, using pure Python fallback for MLP")


@dataclass
class MLPScorer:
    """
    Minimal MLP with deterministic weights and optional numpy acceleration.

    Architecture:
        input (N) -> hidden (H) -> output (1)

    Activation: ReLU for hidden layer, linear for output

    Attributes:
        input_dim: Input feature dimension
        hidden_dim: Hidden layer dimension
        use_numpy: Whether to use numpy for acceleration
    """

    input_dim: int
    hidden_dim: int = 4
    use_numpy: bool = True

    def __post_init__(self):
        """Initialize deterministic weights."""
        # Deterministic initialization for reproducibility
        seed = 42

        if self.use_numpy and NUMPY_AVAILABLE:
            rng = np.random.RandomState(seed)
            self.W1 = rng.randn(self.hidden_dim, self.input_dim) * 0.1
            self.b1 = rng.randn(self.hidden_dim) * 0.01
            self.W2 = rng.randn(1, self.hidden_dim) * 0.1
            self.b2 = rng.randn(1) * 0.01
        else:
            import random

            random.seed(seed)

            # W1: (hidden_dim, input_dim)
            self.W1 = [
                [random.gauss(0, 0.1) for _ in range(self.input_dim)]
                for _ in range(self.hidden_dim)
            ]

            # b1: (hidden_dim,)
            self.b1 = [random.gauss(0, 0.01) for _ in range(self.hidden_dim)]

            # W2: (1, hidden_dim)
            self.W2 = [[random.gauss(0, 0.1) for _ in range(self.hidden_dim)]]

            # b2: (1,)
            self.b2 = [random.gauss(0, 0.01)]

    def score(self, features: Iterable[float]) -> float:
        """
        Score action path features.

        Forward pass:
            h = ReLU(W1 @ x + b1)
            y = W2 @ h + b2

        Args:
            features: Input features (input_dim,)

        Returns:
            Scalar score
        """
        features_list = list(features)

        if len(features_list) != self.input_dim:
            logger.warning(
                f"Feature dimension mismatch: expected {self.input_dim}, "
                f"got {len(features_list)}"
            )
            # Pad or truncate
            if len(features_list) < self.input_dim:
                features_list.extend([0.0] * (self.input_dim - len(features_list)))
            else:
                features_list = features_list[: self.input_dim]

        if self.use_numpy and NUMPY_AVAILABLE:
            x = np.array(features_list)

            # Hidden layer
            h = np.maximum(0, self.W1 @ x + self.b1)  # ReLU

            # Output layer
            y = self.W2 @ h + self.b2

            return float(y[0])
        else:
            # Pure Python fallback

            # Hidden layer: h = ReLU(W1 @ x + b1)
            h = []
            for i in range(self.hidden_dim):
                # Dot product
                activation = sum(
                    w * f for w, f in zip(self.W1[i], features_list)
                )
                activation += self.b1[i]

                # ReLU
                h.append(max(0.0, activation))

            # Output layer: y = W2 @ h + b2
            y = sum(w * h_val for w, h_val in zip(self.W2[0], h))
            y += self.b2[0]

            return y

    def batch_score(self, feature_batch: Iterable[Iterable[float]]) -> list[float]:
        """
        Score multiple feature vectors.

        Args:
            feature_batch: List of feature vectors

        Returns:
            List of scores
        """
        return [self.score(features) for features in feature_batch]
