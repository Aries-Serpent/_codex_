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

# QFT Extensions (Phase C.3 - Path Integral Optimization)
try:
    from .qft import (
        ExecutionPath,
        ActionFunctional,
        PathSampler,
        PathIntegralOptimizer,
        QuantumAnnealingScheduler,
        AdaptivePathOptimizer,
        compare_paths,
        visualize_action_landscape,
    )
    QFT_AVAILABLE = True
except ImportError:
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
    __all__.extend([
        # Phase C.3 - Path Integral Optimization
        "ExecutionPath",
        "ActionFunctional",
        "PathSampler",
        "PathIntegralOptimizer",
        "QuantumAnnealingScheduler",
        "AdaptivePathOptimizer",
        "compare_paths",
        "visualize_action_landscape",
    ])

__version__ = "0.3.0"  # Phase C.3: QFT Path Integral
