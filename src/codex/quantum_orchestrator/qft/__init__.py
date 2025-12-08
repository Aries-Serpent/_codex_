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

from .entanglement import (
    BellState,
    EntangledPair,
    EntanglementManager,
    EntanglementMetrics,
    TransactionalTaskGroup,
)
from .gauge import (
    ConservationEnforcer,
    GaugeChecker,
    NoetherCurrent,
    SymmetryType,
    TimeTranslationSymmetry,
    TransformationResult,
    TranslationSymmetry,
    U1GaugeTransform,
)
from .path_integral import (
    ActionFunctional,
    AdaptivePathOptimizer,
    ExecutionPath,
    PathIntegralOptimizer,
    PathSampler,
    QuantumAnnealingScheduler,
    compare_paths,
    visualize_action_landscape,
)
from .second_quantization import (
    AnnihilationOperator,
    BatchCreationOperator,
    CommutatorAlgebra,
    CreationOperator,
    FockState,
    NumberOperator,
    ParticleStatistics,
    TaskSpawner,
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
