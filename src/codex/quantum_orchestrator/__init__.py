"""
Quantum-Relativistic-Dirac Orchestrator Framework.

A physics-inspired orchestration framework implementing:
- Schrödinger equation dynamics (iℏ∂ψ/∂t = Ĥψ)
- Klein-Gordon relativistic extension (E² = p²c² + m²c⁴)
- Probability current & flow dynamics (∂ρ/∂t + ∇·j = 0)
- Dirac spinor dynamics with 4-component states
- Vectorized performance optimization (Phase 2A)
- MLOps observability integration (Phase 2B)
- Quantum Field Theory extensions (Phase C)

Author: mbaetiong
Generated: 2025-12-08
Version: 0.3.0
"""

import logging

logger = logging.getLogger(__name__)

# Core orchestrator
# MLOps integration
from .mlops_bridge import (
    DistributedCoordinator,
    LoggingAdapter,
    Metric,
    MetricsCollector,
    MetricType,
    ObservableOrchestrator,
    create_observable_orchestrator,
)

# Performance optimization (vectorized operations)
from .optimized import (
    BatchGradientComputer,
    BatchState,
    SpatialIndex,
    VectorizedEvolution,
    apply_batch_state,
    extract_batch_state,
)
from .orchestrator import (
    DiracMatrices,
    DiracOperator,
    DiracSpinor,
    FlowAnalyzer,
    MomentumOperator,
    OrchestratorState,
    PhysicsConstants,
    PotentialLandscape,
    ProbabilityCurrentOperator,
    QuantumRelativisticDiracOrchestrator,
    TaskState,
    TaskVector,
    create_orchestrator,
)

# QFT Extensions (Phases C.1, C.2, C.3)
try:
    from .qft import (  # C.2 - Entanglement; C.3 - Path Integral; C.1 - Second Quantization
        ActionFunctional,
        AdaptivePathOptimizer,
        AnnihilationOperator,
        BatchCreationOperator,
        BellState,
        CreationOperator,
        EntangledPair,
        EntanglementManager,
        ExecutionPath,
        FockState,
        NumberOperator,
        ParticleStatistics,
        PathIntegralOptimizer,
        PathSampler,
        QuantumAnnealingScheduler,
        TaskSpawner,
        TransactionalTaskGroup,
        compare_paths,
        visualize_action_landscape,
    )

    QFT_AVAILABLE = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    QFT_AVAILABLE = False

__all__ = [
    # Phase 1 - Core Physics
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
    # Phase 2A - Performance
    "VectorizedEvolution",
    "BatchState",
    "SpatialIndex",
    "BatchGradientComputer",
    "extract_batch_state",
    "apply_batch_state",
    # Phase 2B - MLOps
    "MetricsCollector",
    "LoggingAdapter",
    "DistributedCoordinator",
    "ObservableOrchestrator",
    "create_observable_orchestrator",
    "MetricType",
    "Metric",
    # QFT availability flag
    "QFT_AVAILABLE",
]

# Conditionally add QFT exports if available
if QFT_AVAILABLE:
    __all__.extend(
        [
            # Phase C.1 - Second Quantization
            "ParticleStatistics",
            "FockState",
            "CreationOperator",
            "AnnihilationOperator",
            "NumberOperator",
            "TaskSpawner",
            "BatchCreationOperator",
            # Phase C.2 - Entanglement
            "BellState",
            "EntangledPair",
            "EntanglementManager",
            "TransactionalTaskGroup",
            # Phase C.3 - Path Integral Optimization
            "ExecutionPath",
            "ActionFunctional",
            "PathSampler",
            "PathIntegralOptimizer",
            "QuantumAnnealingScheduler",
            "AdaptivePathOptimizer",
            "compare_paths",
            "visualize_action_landscape",
        ]
    )

__version__ = "0.3.0"  # Phase C.3: QFT Path Integral
