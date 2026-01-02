"""
Quantum Module - Quantum-Inspired Agent Enhancements

This module provides quantum-inspired features for enhanced agent intelligence:
- Superposition: Parallel decision path exploration
- Entanglement: Correlated agent state management
- Uncertainty: Adaptive test coverage optimization
- Wave Collapse: Accelerated pattern learning

All features are gated by environment variable flags for gradual rollout.
"""

from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.base import QuantumFeature, QuantumState
from cognitive_brain.quantum.coherence_monitor import (
    CoherenceMonitor,
    Alert,
    AlertLevel,
    AlertThreshold
)
from cognitive_brain.quantum.ab_testing import (
    ABTestFramework,
    ExperimentConfig,
    ExperimentResult,
    Variant,
    EXP_1_CONFIG,
    EXP_2_CONFIG,
    EXP_3_CONFIG
)
from cognitive_brain.quantum.superposition import (
    SuperpositionEngine,
    SuperpositionState,
    Decision,
    quantum_superposition
)
from cognitive_brain.quantum.entanglement import (
    EntanglementManager,
    EntangledPair,
    CorrelationMeasurement
)
from cognitive_brain.quantum.uncertainty import (
    UncertaintyOptimizer,
    TestMetrics,
    TestPriority
)

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
    "TestMetrics",
    "TestPriority",
]
