"""
Agents package providing AI-driven orchestration and decision-making tools.

This package contains physics-inspired orchestrators and specialized agents
that use game theory, quantum mechanics, and physical principles to make
optimal decisions.

Modules:
    physics_orchestrator: Physics-inspired decision making with ASSESS → DELIBERATE → OPTIMIZE → ACT workflow
        - Core: PhysicsInspiredOrchestrator, ActionPath, ForceVector, DecisionState
        - Advanced patterns: DiffusionFlowModel, EnergyLandscape, SwarmIntelligence, TaskDecomposer, ReflectionLoop
        - Quantum-Physics Integration: QuantumState, QuantumWalkExplorer, SuperpositionExplorer, 
          PINNValidator, QuantumPhysicsOrchestrator, EntangledDependency
        - Advanced Calculators: QuantumOperator, ConservationLawChecker, PathIntegralCalculator,
          HamiltonianEvolver, PhysicsCalculatorSuite
    quantum_game_theory: Quantum-inspired game theory for Blue Team vs Red Team scenarios
    self_healing: Automated detection, diagnosis, and remediation of CI/CD issues
    mental_mapping: Cognitive framework for storing reasoning chains and decision paths
    workflow_navigator: Tokenized logical workflows for deterministic navigation

Usage:
    # Physics-inspired orchestration
    from agents import PhysicsInspiredOrchestrator, ActionPath, DecisionState
    
    # Import migration automation
    from agents import ImportMigrationOrchestrator, ImportMigration
    
    # Advanced physics patterns
    from agents import DiffusionFlowModel, EnergyLandscape, SwarmIntelligence
    from agents import TaskDecomposer, ReflectionLoop
    
    # Quantum-Physics integration
    from agents import QuantumPhysicsOrchestrator, QuantumState, QuantumWalkExplorer
    from agents import SuperpositionExplorer, PINNValidator, EntangledDependency
    
    # Advanced physics calculators
    from agents import QuantumOperator, ConservationLawChecker, PathIntegralCalculator
    from agents import HamiltonianEvolver, PhysicsCalculatorSuite
    
    # Game theory simulation
    from agents import BlueRedTeamSimulator, QuantumInspiredGameEngine
    
    # Self-healing automation
    from agents import SelfHealingEngine, DetectedIssue
    
    # Mental mapping for reasoning
    from agents import MentalMappingModel, MentalNode
    
    # Workflow navigation
    from agents import WorkflowNavigator, Workflow
"""

# Physics-inspired orchestration
from .physics_orchestrator import (
    ActionPath,
    ActionType,
    DecisionState,
    ForceVector,
    ImportMigration,
    ImportMigrationOrchestrator,
    PhysicsInspiredOrchestrator,
    # Advanced physics patterns
    DiffusionFlowModel,
    EnergyLandscape,
    EnergyState,
    FlowVector,
    ReflectionLoop,
    SubTask,
    SwarmIntelligence,
    SwarmParticle,
    TaskDecomposer,
    # Quantum-Physics Integration
    EntangledDependency,
    PINNValidator,
    QuantumPhysicsOrchestrator,
    QuantumState,
    QuantumWalkExplorer,
    SuperpositionExplorer,
    # Advanced Physics Calculators
    ConservationLawChecker,
    HamiltonianEvolver,
    PathIntegralCalculator,
    PhysicsCalculatorSuite,
    QuantumOperator,
)

# Quantum-inspired game theory
from .quantum_game_theory import (
    BlueRedTeamSimulator,
    ClassicalGameEngine,
    PayoffOperator,
    QuantumGameState,
    QuantumInspiredGameEngine,
    StrategyState,
    TeamType,
)

# Self-healing automation
from .self_healing import (
    DetectedIssue,
    DiagnosticResult,
    IssueSeverity,
    IssueType,
    RemediationAction,
    SelfHealingEngine,
)

# Mental mapping for reasoning chains
from .mental_mapping import (
    EdgeType,
    MentalEdge,
    MentalMappingModel,
    MentalNode,
    NodeType,
    ReasoningStep,
)

# Workflow navigation
from .workflow_navigator import (
    StepStatus,
    Workflow,
    WorkflowFrequency,
    WorkflowNavigator,
    WorkflowStep,
)

__all__ = [
    # Physics orchestrator - Core
    "ActionPath",
    "ActionType",
    "DecisionState",
    "ForceVector",
    "ImportMigration",
    "ImportMigrationOrchestrator",
    "PhysicsInspiredOrchestrator",
    # Physics orchestrator - Advanced Patterns
    "DiffusionFlowModel",
    "EnergyLandscape",
    "EnergyState",
    "FlowVector",
    "ReflectionLoop",
    "SubTask",
    "SwarmIntelligence",
    "SwarmParticle",
    "TaskDecomposer",
    # Physics orchestrator - Quantum-Physics Integration
    "EntangledDependency",
    "PINNValidator",
    "QuantumPhysicsOrchestrator",
    "QuantumState",
    "QuantumWalkExplorer",
    "SuperpositionExplorer",
    # Physics orchestrator - Advanced Calculators
    "ConservationLawChecker",
    "HamiltonianEvolver",
    "PathIntegralCalculator",
    "PhysicsCalculatorSuite",
    "QuantumOperator",
    # Quantum game theory
    "BlueRedTeamSimulator",
    "ClassicalGameEngine",
    "PayoffOperator",
    "QuantumGameState",
    "QuantumInspiredGameEngine",
    "StrategyState",
    "TeamType",
    # Self-healing
    "DetectedIssue",
    "DiagnosticResult",
    "IssueSeverity",
    "IssueType",
    "RemediationAction",
    "SelfHealingEngine",
    # Mental mapping
    "EdgeType",
    "MentalEdge",
    "MentalMappingModel",
    "MentalNode",
    "NodeType",
    "ReasoningStep",
    # Workflow navigator
    "StepStatus",
    "Workflow",
    "WorkflowFrequency",
    "WorkflowNavigator",
    "WorkflowStep",
]
