"""
Quantum-Relativistic-Dirac Orchestrator Framework.

A physics-inspired orchestration framework implementing:
- Schrödinger equation dynamics (iℏ∂ψ/∂t = Ĥψ)
- Klein-Gordon relativistic extension (E² = p²c² + m²c⁴)
- Probability current & flow dynamics
- Dirac spinor dynamics with 4-component states

Author: mbaetiong
Generated: 2025-12-08
"""

# Import everything from the consolidated orchestrator module
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

__all__ = [
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
]

__version__ = "0.1.0"
