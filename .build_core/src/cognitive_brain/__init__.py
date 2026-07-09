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

from . import quantum

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
        "ActionResult",
        "Decision",
        "MemoryInterface",
        "ObservationData",
        "OrientationResult",
        "PhysicsOfThought",
        "Planner",
        "quantum",
    ]
else:
    __all__ = ["quantum"]
