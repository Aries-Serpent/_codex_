"""Brain module — Session checkpoint and recovery framework.

Phase 10.1: Provides checkpoint management, session serialization, and
recovery capabilities for autonomous agent persistence.

Components:
- CheckpointManager: Manages checkpoint lifecycle
- SessionSerializer: Serializes/deserializes session state
- SessionResume: Restores sessions from checkpoints
"""

from __future__ import annotations

from codex.brain.checkpoint_manager import CheckpointManager
from codex.brain.session_resume import SessionResume, ResumeResult
from codex.brain.session_serializer import (
    SessionSerializer,
    AgentStateSnapshot,
    DecisionSnapshot,
    MemorySnapshot,
    ExecutionProgressSnapshot,
    RepositoryStateSnapshot,
    ContextSnapshot,
    create_agent_state_snapshot,
    create_decision_snapshot,
    create_memory_snapshot,
    create_execution_progress_snapshot,
    create_repository_state_snapshot,
    create_context_snapshot,
)

# Phase 10.3: OODA Orchestration
try:
    from codex.brain.ooda_observer import (
        OODAObserver,
        Observable,
        RepositoryState,
        AgentEcosystemState,
        TaskQueueState,
        EnvironmentMetrics,
    )
    from codex.brain.ooda_orienter import (
        OODAOrienter,
        Orientation,
        Pattern,
        RiskAssessment,
    )
    from codex.brain.ooda_decider import (
        OODADecider,
        DecisionDirective,
        DecisionType,
    )
    from codex.brain.ooda_actor import (
        OODAactor,
        ExecutionReport,
    )
    from codex.brain.ooda_orchestrator import (
        OODAOrchestrator,
        ParallelOODAOrchestrator,
        CycleRecord,
        OODAMetrics,
    )
    OODA_AVAILABLE = True
except ImportError:
    OODA_AVAILABLE = False

__all__ = [
    "CheckpointManager",
    "SessionResume",
    "ResumeResult",
    "SessionSerializer",
    "AgentStateSnapshot",
    "DecisionSnapshot",
    "MemorySnapshot",
    "ExecutionProgressSnapshot",
    "RepositoryStateSnapshot",
    "ContextSnapshot",
    "create_agent_state_snapshot",
    "create_decision_snapshot",
    "create_memory_snapshot",
    "create_execution_progress_snapshot",
    "create_repository_state_snapshot",
    "create_context_snapshot",
]

# Add OODA components if available
if OODA_AVAILABLE:
    __all__.extend([
        "OODAObserver",
        "Observable",
        "RepositoryState",
        "AgentEcosystemState",
        "TaskQueueState",
        "EnvironmentMetrics",
        "OODAOrienter",
        "Orientation",
        "Pattern",
        "RiskAssessment",
        "OODADecider",
        "DecisionDirective",
        "DecisionType",
        "OODAactor",
        "ExecutionReport",
        "OODAOrchestrator",
        "ParallelOODAOrchestrator",
        "CycleRecord",
        "OODAMetrics",
    ])
