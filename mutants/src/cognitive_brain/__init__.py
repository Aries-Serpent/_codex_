"""
Cognitive Brain Framework - Quantum-Enhanced Agent Intelligence

This package provides the core infrastructure for quantum-inspired enhancements
to the agent cognitive framework, enabling advanced decision-making capabilities
through superposition, entanglement, uncertainty optimization, and wave collapse.

Part of Phase 1: Split Brain Resolution - provides the foundation
for unifying legacy agents/ with modern cognitive architecture.

Version: 0.1.0 (Phase 7.1)
Status: Infrastructure Setup with ABCs
"""

from __future__ import annotations

# Export base classes for agent inheritance
try:
    from .base import (
        ActionResult,
        Decision,
        MemoryInterface,
        ObservationData,
        OrientationResult,
        PhysicsOfThought,
        Planner,
    )

    _base_available = True
except ImportError:
    # Base module not yet available in all environments
    _base_available = False

__version__ = "0.1.0"

if _base_available:
    __all__ = [
        "quantum",
        "Planner",
        "MemoryInterface",
        "PhysicsOfThought",
        "ObservationData",
        "OrientationResult",
        "Decision",
        "ActionResult",
    ]
else:
    __all__ = ["quantum"]
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
