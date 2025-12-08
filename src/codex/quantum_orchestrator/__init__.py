"""
Quantum-Relativistic-Dirac Orchestrator Framework.

A physics-inspired orchestration framework implementing:
- Schrödinger equation dynamics (iℏ∂ψ/∂t = Ĥψ)
- Klein-Gordon relativistic extension (E² = p²c² + m²c⁴)
- Probability current & flow dynamics
- Dirac spinor dynamics with 4-component states
- Vectorized performance optimization
- MLOps observability integration

Author: mbaetiong
Generated: 2025-12-08
"""

# Core orchestrator
from .orchestrator import (
    PhysicsConstants,
    TaskVector,
    DiracSpinor,
    DiracMatrices,
    TaskState,
    DiracOperator,
    MomentumOperator,
    PotentialLandscape,
    ProbabilityCurrentOperator,
    FlowAnalyzer,
    OrchestratorState,
    QuantumRelativisticDiracOrchestrator,
    create_orchestrator,
)

# Performance optimization (vectorized operations)
from .optimized import (
    VectorizedEvolution,
    BatchState,
    SpatialIndex,
    BatchGradientComputer,
    extract_batch_state,
    apply_batch_state,
)

# MLOps integration
from .mlops_bridge import (
    MetricsCollector,
    LoggingAdapter,
    DistributedCoordinator,
    ObservableOrchestrator,
    create_observable_orchestrator,
    MetricType,
    Metric,
)

__all__ = [
    # Core
    "PhysicsConstants",
    "TaskVector",
    "DiracSpinor",
    "DiracMatrices",
    "TaskState",
    "DiracOperator",
    "MomentumOperator",
    "PotentialLandscape",
    "ProbabilityCurrentOperator",
    "FlowAnalyzer",
    "OrchestratorState",
    "QuantumRelativisticDiracOrchestrator",
    "create_orchestrator",
    # Performance
    "VectorizedEvolution",
    "BatchState",
    "SpatialIndex",
    "BatchGradientComputer",
    "extract_batch_state",
    "apply_batch_state",
    # MLOps
    "MetricsCollector",
    "LoggingAdapter",
    "DistributedCoordinator",
    "ObservableOrchestrator",
    "create_observable_orchestrator",
    "MetricType",
    "Metric",
]

__version__ = "0.2.0"  # Phase 2 enhancements
