"""
Codex Cognitive Brain Module

This module provides the cognitive brain infrastructure for AI agent coordination,
including:
- AgentBrainInterface: Standard interface for agent-brain communication
- Pattern learning and retrieval
- Session state management
- Objective tracking
"""

from codex.cognitive.agent_brain_api import (
    AGENT_CAPABILITIES,
    AgentBrainAPI,
    AgentSessionContext,
    CognitiveBrain,
    CompletionReport,
)
from codex.cognitive.brain_interface import (
    AgentBrainInterface,
    AgentContext,
    BrainResponse,
    LearningFeedback,
    PatternMatch,
)
from codex.cognitive.planset_orchestrator import (
    OrchestrationState,
    PlansetOrchestrator,
    PlansetRecord,
    PromptSet,
)
from codex.cognitive.quantum_planset_engine import (
    ImprovementArea,
    PhysicsParams,
    PlanStep,
    QuantumPlanset,
    QuantumPlansetEngine,
    StepStatus,
)

# ---------------------------------------------------------------------------
# Module-level singleton — the single intuitive entry-point for all AI agents.
#
#   from codex.cognitive import brain
#
#   ctx  = brain.session("my-agent-id")
#   next = brain.next()
#   brain.advance("SECURITY_REMEDIATION", "SEC-01")
#   print(brain.help())
#   print(brain.discover())
# ---------------------------------------------------------------------------
brain: CognitiveBrain = CognitiveBrain()

__all__ = [
    # ── Primary singleton ──────────────────────────────────────────────
    "brain",
    # ── Agent Brain API ───────────────────────────────────────────────
    "AgentBrainAPI",
    "AgentSessionContext",
    "CompletionReport",
    "CognitiveBrain",
    "AGENT_CAPABILITIES",
    # ── Brain interface ───────────────────────────────────────────────
    "AgentBrainInterface",
    "AgentContext",
    "PatternMatch",
    "LearningFeedback",
    "BrainResponse",
    # ── Planset orchestrator ──────────────────────────────────────────
    "PlansetOrchestrator",
    "PlansetRecord",
    "PromptSet",
    "OrchestrationState",
    # ── Quantum engine ────────────────────────────────────────────────
    "ImprovementArea",
    "PhysicsParams",
    "PlanStep",
    "QuantumPlanset",
    "QuantumPlansetEngine",
    "StepStatus",
]

__version__ = "1.0.0"
