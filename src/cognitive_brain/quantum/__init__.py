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
    "EXP_1_CONFIG",
    "EXP_2_CONFIG",
    "EXP_3_CONFIG",
    "ABTestFramework",
    "Alert",
    "AlertLevel",
    "AlertThreshold",
    "CoherenceMonitor",
    "CorrelationMeasurement",
    "Decision",
    "EntangledPair",
    "EntanglementManager",
    "ExecutionMetrics",
    "ExecutionPriority",
    "ExperimentConfig",
    "ExperimentResult",
    "QuantumConfig",
    "QuantumFeature",
    "QuantumState",
    "SuperpositionEngine",
    "SuperpositionState",
    "TestExecutionMetrics",  # Backward compatibility alias
    "TestExecutionPriority",  # Backward compatibility alias
    "TestMetrics",  # Backward compatibility alias
    "TestPriority",  # Backward compatibility alias
    "UncertaintyOptimizer",
    "Variant",
    "quantum_superposition",
]
