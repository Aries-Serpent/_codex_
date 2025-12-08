"""
Quantum Field Theory extensions for quantum orchestrator.

Includes:
- Second quantization (task spawning)
- Quantum entanglement (Bell states)
- Path integral optimization
- Quantum annealing
- Action functionals
- Gauge symmetries and conservation laws
"""

from .second_quantization import (
    ParticleStatistics,
    FockState,
    CreationOperator,
    AnnihilationOperator,
    NumberOperator,
    CommutatorAlgebra,
    TaskSpawner,
    BatchCreationOperator,
)

from .entanglement import (
    BellState,
    EntangledPair,
    EntanglementMetrics,
    EntanglementManager,
    TransactionalTaskGroup,
)

from .path_integral import (
    ExecutionPath,
    ActionFunctional,
    PathSampler,
    PathIntegralOptimizer,
    QuantumAnnealingScheduler,
    AdaptivePathOptimizer,
    compare_paths,
    visualize_action_landscape,
)

from .gauge import (
    SymmetryType,
    TransformationResult,
    U1GaugeTransform,
    TranslationSymmetry,
    TimeTranslationSymmetry,
    NoetherCurrent,
    GaugeChecker,
    ConservationEnforcer,
)

__all__ = [
    # Second Quantization
    "ParticleStatistics",
    "FockState",
    "CreationOperator",
    "AnnihilationOperator",
    "NumberOperator",
    "CommutatorAlgebra",
    "TaskSpawner",
    "BatchCreationOperator",
    # Entanglement
    "BellState",
    "EntangledPair",
    "EntanglementMetrics",
    "EntanglementManager",
    "TransactionalTaskGroup",
    # Path Integral
    "ExecutionPath",
    "ActionFunctional",
    "PathSampler",
    "PathIntegralOptimizer",
    "QuantumAnnealingScheduler",
    "AdaptivePathOptimizer",
    "compare_paths",
    "visualize_action_landscape",
    # Gauge Symmetries
    "SymmetryType",
    "TransformationResult",
    "U1GaugeTransform",
    "TranslationSymmetry",
    "TimeTranslationSymmetry",
    "NoetherCurrent",
    "GaugeChecker",
    "ConservationEnforcer",
]
