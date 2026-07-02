"""Brain module — Cognitive agent framework with memory and orchestration.

Phase 10.1: Session checkpoint and recovery framework.
- CheckpointManager: Manages checkpoint lifecycle
- SessionSerializer: Serializes/deserializes session state
- SessionResume: Restores sessions from checkpoints

Phase 10.2: STM→LTM Memory Consolidation & Pattern Discovery.
- MemorySyncEngine: STM→LTM consolidation with pattern scoring
- Pattern discovery and automatic ImprovementArea tagging
- Safe deletion audit trail and retention policies

Phase 10.3: OODA Orchestration (optional).
"""

from __future__ import annotations

from codex.brain.checkpoint_manager import CheckpointManager
from codex.brain.session_resume import ResumeResult, SessionResume
from codex.brain.session_serializer import (
    AgentStateSnapshot,
    ContextSnapshot,
    DecisionSnapshot,
    ExecutionProgressSnapshot,
    MemorySnapshot,
    RepositoryStateSnapshot,
    SessionSerializer,
    create_agent_state_snapshot,
    create_context_snapshot,
    create_decision_snapshot,
    create_execution_progress_snapshot,
    create_memory_snapshot,
    create_repository_state_snapshot,
)

# Phase 10.2: Memory Synchronization
try:
    from codex.brain.memory_sync import (
        ConsolidationMetrics,
        DuplicateMatch,
        ImprovementArea,
        MemorySyncEngine,
        PatternEntry,
        PatternType,
        RetentionPolicy,
    )

    MEMORY_SYNC_AVAILABLE = True
except ImportError:
    MEMORY_SYNC_AVAILABLE = False

# Phase 10.3: OODA Orchestration
try:
    from codex.brain.ooda_actor import (
        ExecutionReport,
        OODAactor,
    )
    from codex.brain.ooda_decider import (
        DecisionDirective,
        DecisionType,
        OODADecider,
    )
    from codex.brain.ooda_observer import (
        AgentEcosystemState,
        EnvironmentMetrics,
        Observable,
        OODAObserver,
        RepositoryState,
        TaskQueueState,
    )
    from codex.brain.ooda_orchestrator import (
        CycleRecord,
        OODAMetrics,
        OODAOrchestrator,
        ParallelOODAOrchestrator,
    )
    from codex.brain.ooda_orienter import (
        OODAOrienter,
        Orientation,
        Pattern,
        RiskAssessment,
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

# Phase 10.2: Memory Synchronization (if available)
if MEMORY_SYNC_AVAILABLE:
    __all__.extend(
        [
            "MemorySyncEngine",
            "PatternEntry",
            "PatternType",
            "RetentionPolicy",
            "ImprovementArea",
            "ConsolidationMetrics",
            "DuplicateMatch",
        ]
    )

# Phase 10.3: OODA Orchestration
if OODA_AVAILABLE:
    __all__.extend(
        [
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
        ]
    )
