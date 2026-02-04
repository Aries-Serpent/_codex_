"""
Quantum Module - Quantum-Inspired Agent Enhancements

This module provides quantum-inspired features for enhanced agent intelligence:
- Superposition: Parallel decision path exploration
- Entanglement: Correlated agent state management
- Uncertainty: Adaptive test coverage optimization
- Wave Collapse: Accelerated pattern learning

All features are gated by environment variable flags for gradual rollout.
"""

from cognitive_brain.quantum.ab_testing import (
    EXP_1_CONFIG,
    EXP_2_CONFIG,
    EXP_3_CONFIG,
    ABTestFramework,
    ExperimentConfig,
    ExperimentResult,
    Variant,
)
from cognitive_brain.quantum.base import QuantumFeature, QuantumState
from cognitive_brain.quantum.coherence_monitor import (
    Alert,
    AlertLevel,
    AlertThreshold,
    CoherenceMonitor,
)
from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.entanglement import (
    CorrelationMeasurement,
    EntangledPair,
    EntanglementManager,
)
from cognitive_brain.quantum.superposition import (
    Decision,
    SuperpositionEngine,
    SuperpositionState,
    quantum_superposition,
)
from cognitive_brain.quantum.uncertainty import (
    ExecutionMetrics,
    ExecutionPriority,
    UncertaintyOptimizer,
)

# Backward compatibility aliases
TestExecutionMetrics = ExecutionMetrics
TestExecutionPriority = ExecutionPriority
TestMetrics = ExecutionMetrics
TestPriority = ExecutionPriority

__version__ = "0.1.0"
__all__ = [
    "QuantumConfig",
    "QuantumFeature",
    "QuantumState",
    "CoherenceMonitor",
    "Alert",
    "AlertLevel",
    "AlertThreshold",
    "ABTestFramework",
    "ExperimentConfig",
    "ExperimentResult",
    "Variant",
    "EXP_1_CONFIG",
    "EXP_2_CONFIG",
    "EXP_3_CONFIG",
    "SuperpositionEngine",
    "SuperpositionState",
    "Decision",
    "quantum_superposition",
    "EntanglementManager",
    "EntangledPair",
    "CorrelationMeasurement",
    "UncertaintyOptimizer",
    "ExecutionMetrics",
    "ExecutionPriority",
    "TestExecutionMetrics",  # Backward compatibility alias
    "TestExecutionPriority",  # Backward compatibility alias
    "TestMetrics",  # Backward compatibility alias
    "TestPriority",  # Backward compatibility alias
]
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
