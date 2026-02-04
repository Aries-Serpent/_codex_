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
