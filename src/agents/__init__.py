"""Compatibility package for the repo-root `agents` namespace.

The repo keeps a src-first pytest config (`pythonpath = src agents/codex_client`).
The canonical human-facing agent modules still live under the repository-root
`agents/` directory, while the `src/agents` package is the importable compatibility
surface for the editable install. This shim preserves the historical public API and
prevents collection from failing on package-boundary drift.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_ROOT_AGENTS = _ROOT / "agents"
__path__ = [str(Path(__file__).resolve().parent), str(_ROOT_AGENTS)]
__version__ = "0.0.0"
__all__: list[str] = ["__version__"]

for _module_name in (
   "mental_mapping",
   "physics_orchestrator",
   "quantum_game_theory",
   "self_healing",
   "workflow_navigator",
   "developer_orchestrator",
   "agent_memory",
   "msp_client",
   "exceptions",
   "physics_integration",
   "agent_memory",
):
   try:
       _module = import_module(f"{__name__}.{_module_name}")
   except ModuleNotFoundError:
       continue
   for _name in getattr(_module, "__all__", []):
       if _name.startswith("_"):
           continue
       globals()[_name] = getattr(_module, _name)
       if _name not in __all__:
           __all__.append(_name)

for _name in (
   "ActionPath",
   "ActionType",
   "DecisionState",
   "ForceVector",
   "ImportMigration",
   "ImportMigrationOrchestrator",
   "PhysicsInspiredOrchestrator",
   "DiffusionFlowModel",
   "EnergyLandscape",
   "EnergyState",
   "ReflectionLoop",
   "SubTask",
   "SwarmIntelligence",
   "SwarmParticle",
   "TaskDecomposer",
   "EntangledDependency",
   "PINNValidator",
   "QuantumPhysicsOrchestrator",
   "QuantumState",
   "QuantumWalkExplorer",
   "SuperpositionExplorer",
   "ConservationLawChecker",
   "HamiltonianEvolver",
   "PathIntegralCalculator",
   "PhysicsCalculatorSuite",
   "QuantumOperator",
   "BlueRedTeamSimulator",
   "ClassicalGameEngine",
   "PayoffOperator",
   "QuantumGameState",
   "QuantumInspiredGameEngine",
   "StrategyState",
   "TeamType",
   "DetectedIssue",
   "DiagnosticResult",
   "IssueSeverity",
   "IssueType",
   "RemediationAction",
   "SelfHealingEngine",
   "EdgeType",
   "MentalEdge",
   "MentalMappingModel",
   "MentalNode",
   "NodeType",
   "ReasoningStep",
   "get_timestamp",
   "reset_clock",
   "set_clock",
   "StepStatus",
   "Workflow",
   "WorkflowFrequency",
   "WorkflowNavigator",
   "WorkflowStep",
   "Agent",
   "AgentOrchestrator",
   "AgentStatus",
   "RateLimiter",
):
   if _name not in globals():
       continue
   if _name not in __all__:
       __all__.append(_name)


def __getattr__(name: str):
   """Lazily resolve historically expected agent modules from the repo-root package."""
   if name.startswith("_"):
       raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
   try:
       module = import_module(f"{__name__}.{name}")
   except ModuleNotFoundError as exc:
       raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
   globals()[name] = module
   return module
