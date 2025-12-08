"""
Quantum Field Theory extensions for quantum orchestrator.

Includes:
- Second quantization (task spawning)
- Path integral optimization
- Quantum annealing
- Action functionals
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
    # Path Integral
    "ExecutionPath",
    "ActionFunctional",
    "PathSampler",
    "PathIntegralOptimizer",
    "QuantumAnnealingScheduler",
    "AdaptivePathOptimizer",
    "compare_paths",
    "visualize_action_landscape",
]
