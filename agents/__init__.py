"""
Agents package providing AI-driven orchestration and decision-making tools.

This package contains physics-inspired orchestrators and specialized agents
that use game theory, quantum mechanics, and physical principles to make
optimal decisions.

Modules:
    physics_orchestrator: Physics-inspired decision making with ASSESS → DELIBERATE → OPTIMIZE → ACT workflow
        - Includes advanced patterns: DiffusionFlowModel, EnergyLandscape, SwarmIntelligence, TaskDecomposer, ReflectionLoop
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
