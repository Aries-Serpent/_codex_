"""
Quantum Base Classes

Provides base classes and enums for quantum-inspired features.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict
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
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate state after initialization."""
        if self.metadata is None:
            self.metadata = {}

        if not 0.0 <= self.coherence <= 1.0:
            raise ValueError(
                f"Coherence must be between 0.0 and 1.0, got {self.coherence}"
            )

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
            raise ValueError(
                f"Coherence must be between 0.0 and 1.0, got {new_coherence}"
            )
        self.coherence = new_coherence

    def to_dict(self) -> Dict[str, Any]:
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
        return (
            f"QuantumState(feature={self.feature.value}, "
            f"coherence={self.coherence:.3f})"
        )


class QuantumException(Exception):
    """Base exception for quantum feature errors."""

    pass


class CoherenceDegradationError(QuantumException):
    """Raised when quantum state coherence drops below acceptable threshold."""

    def xǁCoherenceDegradationErrorǁ__init____mutmut_orig(self, current: float, threshold: float, feature: str):
        self.current = current
        self.threshold = threshold
        self.feature = feature
        super().__init__(
            f"Coherence degradation detected in {feature}: "
            f"{current:.3f} < {threshold:.3f}"
        )

    def xǁCoherenceDegradationErrorǁ__init____mutmut_1(self, current: float, threshold: float, feature: str):
        self.current = None
        self.threshold = threshold
        self.feature = feature
        super().__init__(
            f"Coherence degradation detected in {feature}: "
            f"{current:.3f} < {threshold:.3f}"
        )

    def xǁCoherenceDegradationErrorǁ__init____mutmut_2(self, current: float, threshold: float, feature: str):
        self.current = current
        self.threshold = None
        self.feature = feature
        super().__init__(
            f"Coherence degradation detected in {feature}: "
            f"{current:.3f} < {threshold:.3f}"
        )

    def xǁCoherenceDegradationErrorǁ__init____mutmut_3(self, current: float, threshold: float, feature: str):
        self.current = current
        self.threshold = threshold
        self.feature = None
        super().__init__(
            f"Coherence degradation detected in {feature}: "
            f"{current:.3f} < {threshold:.3f}"
        )

    def xǁCoherenceDegradationErrorǁ__init____mutmut_4(self, current: float, threshold: float, feature: str):
        self.current = current
        self.threshold = threshold
        self.feature = feature
        super().__init__(
            None
        )
    
    xǁCoherenceDegradationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCoherenceDegradationErrorǁ__init____mutmut_1': xǁCoherenceDegradationErrorǁ__init____mutmut_1, 
        'xǁCoherenceDegradationErrorǁ__init____mutmut_2': xǁCoherenceDegradationErrorǁ__init____mutmut_2, 
        'xǁCoherenceDegradationErrorǁ__init____mutmut_3': xǁCoherenceDegradationErrorǁ__init____mutmut_3, 
        'xǁCoherenceDegradationErrorǁ__init____mutmut_4': xǁCoherenceDegradationErrorǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCoherenceDegradationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCoherenceDegradationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCoherenceDegradationErrorǁ__init____mutmut_orig)
    xǁCoherenceDegradationErrorǁ__init____mutmut_orig.__name__ = 'xǁCoherenceDegradationErrorǁ__init__'


class InvalidQuantumConfigurationError(QuantumException):
    """Raised when quantum configuration is invalid."""

    pass
