"""
Quantum Base Classes

Provides base classes and enums for quantum-inspired features.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class QuantumFeature(Enum):
    """Enumeration of available quantum features."""

    SUPERPOSITION = "superposition"
    ENTANGLEMENT = "entanglement"
    UNCERTAINTY = "uncertainty"
    WAVE_COLLAPSE = "wave_collapse"

    def __str__(self) -> str:
        return self.value


@dataclass
class QuantumState:
    """
    Base class for quantum-inspired state representations.

    This class provides a common interface for different quantum features
    to represent and manipulate agent states.

    Attributes:
        feature: The quantum feature this state represents
        coherence: Measure of state coherence (0.0 to 1.0)
        metadata: Additional feature-specific metadata
    """

    feature: QuantumFeature
    coherence: float = 1.0
    metadata: dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self):
        """Validate state after initialization."""
        if self.metadata is None:
            self.metadata = {}

        if not 0.0 <= self.coherence <= 1.0:
            raise ValueError(f"Coherence must be between 0.0 and 1.0, got {self.coherence}")

    def is_coherent(self, threshold: float = 0.3) -> bool:
        """
        Check if state maintains sufficient coherence.

        Args:
            threshold: Minimum coherence level (default: 0.3)

        Returns:
            True if coherence >= threshold, False otherwise
        """
        return self.coherence >= threshold

    def update_coherence(self, new_coherence: float) -> None:
        """
        Update the coherence value.

        Args:
            new_coherence: New coherence value (0.0 to 1.0)

        Raises:
            ValueError: If new_coherence is out of range
        """
        if not 0.0 <= new_coherence <= 1.0:
            raise ValueError(f"Coherence must be between 0.0 and 1.0, got {new_coherence}")
        self.coherence = new_coherence

    def to_dict(self) -> dict[str, Any]:
        """
        Convert state to dictionary representation.

        Returns:
            Dictionary with state data
        """
        return {
            "feature": str(self.feature),
            "coherence": self.coherence,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        """String representation of quantum state."""
        return f"QuantumState(feature={self.feature.value}, coherence={self.coherence:.3f})"


class QuantumException(Exception):
    """Base exception for quantum feature errors."""


class CoherenceDegradationError(QuantumException):
    """Raised when quantum state coherence drops below acceptable threshold."""

    def __init__(self, current: float, threshold: float, feature: str):
        self.current = current
        self.threshold = threshold
        self.feature = feature
        super().__init__(
            f"Coherence degradation detected in {feature}: {current:.3f} < {threshold:.3f}"
        )


class InvalidQuantumConfigurationError(QuantumException):
    """Raised when quantum configuration is invalid."""
