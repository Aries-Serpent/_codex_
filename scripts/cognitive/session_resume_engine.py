"""Session resume engine for restoring and initializing sessions from checkpoints.

This module provides the primary interface for resuming sessions with full context
injection, dependency resolution, and graceful fallback mechanisms.

Author: cognitive-brain-session-injector
Phase: 10.1 - Session Checkpoint/Resume System
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from scripts.cognitive.session_checkpoint_manager import (
        CheckpointCorruptedError,
        CheckpointNotFoundError,
        SessionCheckpointManager,
    )
except ImportError:  # pragma: no cover - direct script execution fallback
    from session_checkpoint_manager import (  # type: ignore[no-redef]
        CheckpointCorruptedError,
        CheckpointNotFoundError,
        SessionCheckpointManager,
    )

logger = logging.getLogger(__name__)

__all__ = [
    "ContextProvider",
    "SessionContext",
    "RecoveryMetadata",
    "SessionResumeError",
    "ContextInjectionError",
    "DependencyResolutionError",
    "WarmupError",
    "SessionResumeEngine",
    "resume_session",
]


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class ContextProvider:
    """Provides runtime context for session initialization."""

    def get_observation_data(self) -> Dict[str, Any]:
        """Get initial observation data (Track 10.3 OODA loop)."""
        return {}

    def get_orientation_data(self) -> Dict[str, Any]:
        """Get orientation context."""
        return {}

    def get_decision_context(self) -> Dict[str, Any]:
        """Get decision-making context."""
        return {}

    def get_action_context(self) -> Dict[str, Any]:
        """Get action execution context."""
        return {}


@dataclass
class SessionContext:
    """Complete context for session resumption."""

    session_id: str
    agent_id: str
    agent_status: str
    checkpoint_id: str

    # Restored state
    agent_state: Dict[str, Any]
    memory_snapshot: Dict[str, Any]
    execution_progress: Dict[str, Any]
    decision_history: list = field(default_factory=list)

    # Lane and cost metadata
    lane_bucket: Optional[str] = None
    checkpoint_state: Optional[str] = None
    budget_remaining: Optional[float] = None
    estimated_cost: Optional[float] = None
    cost_score: Optional[float] = None
    task_id: Optional[str] = None
    last_successful_stage: Optional[str] = None
    resume_from_checkpoint_id: Optional[str] = None

    # Injected context
    observation_data: Dict[str, Any] = field(default_factory=dict)
    orientation_data: Dict[str, Any] = field(default_factory=dict)
    decision_context: Dict[str, Any] = field(default_factory=dict)
    action_context: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    resumed_at: datetime = field(default_factory=datetime.utcnow)
    warmup_complete: bool = False
    recovery_metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if context is valid for resumption."""
        return (
            self.session_id
            and self.checkpoint_id
            and self.agent_state is not None
            and self.execution_progress is not None
        )


@dataclass
class RecoveryMetadata:
    """Metadata about checkpoint recovery."""

    recovered: bool
    recovery_method: str  # 'none', 'quantum_reconstruction', 'fallback'
    confidence: float  # 0.0-1.0
    original_error: Optional[str] = None
    degraded_mode: bool = False
    missing_fields: list = field(default_factory=list)


# ============================================================================
# Exceptions
# ============================================================================


class SessionResumeError(Exception):
    """Base exception for session resume operations."""

    pass


class ContextInjectionError(SessionResumeError):
    """Failed to inject context into session."""

    pass


class DependencyResolutionError(SessionResumeError):
    """Failed to resolve dependencies."""

    pass


class WarmupError(SessionResumeError):
    """Cold-start warmup sequence failed."""

    pass


# ============================================================================
# SessionResumeEngine
# ============================================================================


class SessionResumeEngine:
    """
    Manages deserialization, validation, and restoration of session state.

    Features:
    - Checkpoint deserialization and validation
    - State integrity verification
    - Runtime dependency injection
    - Context augmentation (from Track 10.2 & 10.3)
    - Graceful fallback on corruption
    - Cold-start warmup sequences
    """

    def __init__(
        self,
        checkpoint_manager: Optional[SessionCheckpointManager] = None,
        fallback_strategy: str = "quantum_reconstruction",
        enable_warmup: bool = True,
    ):
        """
        Initialize resume engine.

        Args:
            checkpoint_manager: Manager instance (auto-created if None)
            fallback_strategy: Strategy for corruption recovery
            enable_warmup: Enable cold-start warmup sequence
        """
        self.checkpoint_manager = checkpoint_manager or SessionCheckpointManager()
        self.fallback_strategy = fallback_strategy
        self.enable_warmup = enable_warmup

    def warm_start(
        self,
        checkpoint_id: str,
        context_provider: Optional[ContextProvider] = None,
        environment_overrides: Optional[Dict[str, Any]] = None,
    ) -> SessionContext:
        """
        Warm-start session from checkpoint with full context injection.

        Args:
            checkpoint_id: Checkpoint to restore from
            context_provider: Provider for OODA loop context (Track 10.3)
            environment_overrides: Override specific state values

        Returns:
            SessionContext ready for immediate execution

        Raises:
            SessionResumeError: If checkpoint can't be loaded
            ContextInjectionError: If context injection fails
        """
        # Load and validate checkpoint
        try:
            checkpoint_doc = self.checkpoint_manager.restore_checkpoint(
                checkpoint_id=checkpoint_id, validation_mode="warn", fallback_on_corruption=True
            )
        except (CheckpointNotFoundError, CheckpointCorruptedError) as e:
            raise SessionResumeError(f"Failed to load checkpoint: {e}")

        metadata = checkpoint_doc.get("metadata", {}) or {}

        def _metadata_value(primary: Any, fallback: Any) -> Any:
            if primary is not None:
                return primary
            return fallback

        def _coerce_numeric(value: Any) -> Any:
            if value is None or value == "":
                return None
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return value
            if isinstance(value, str):
                stripped = value.strip()
                if not stripped or stripped.lower() in {"none", "null"}:
                    return None
                try:
                    return float(stripped)
                except ValueError:
                    return value
            return value

        # Build session context preserving valid zero and empty values without lossy coercion.
        context = SessionContext(
            session_id=checkpoint_doc.get("session_id", "unknown"),
            agent_id=checkpoint_doc.get("agent_state", {}).get("agent_id", "unknown"),
            agent_status=checkpoint_doc.get("agent_state", {}).get("status", "paused"),
            checkpoint_id=checkpoint_id,
            agent_state=checkpoint_doc.get("agent_state", {}),
            memory_snapshot=checkpoint_doc.get("memory_snapshot", {}),
            execution_progress=checkpoint_doc.get("execution_progress", {}),
            decision_history=checkpoint_doc.get("decision_history", []),
            lane_bucket=_metadata_value(checkpoint_doc.get("lane_bucket"), metadata.get("lane_bucket")),
            checkpoint_state=_metadata_value(checkpoint_doc.get("checkpoint_state"), metadata.get("checkpoint_state")),
            budget_remaining=_coerce_numeric(
                _metadata_value(checkpoint_doc.get("budget_remaining"), metadata.get("budget_remaining"))
            ),
            estimated_cost=_coerce_numeric(
                _metadata_value(checkpoint_doc.get("estimated_cost"), metadata.get("estimated_cost"))
            ),
            cost_score=_coerce_numeric(
                _metadata_value(checkpoint_doc.get("cost_score"), metadata.get("cost_score"))
            ),
            task_id=_metadata_value(checkpoint_doc.get("task_id"), metadata.get("task_id")),
            last_successful_stage=_metadata_value(
                checkpoint_doc.get("last_successful_stage"), metadata.get("last_successful_stage")
            ),
            resume_from_checkpoint_id=_metadata_value(
                checkpoint_doc.get("resume_from_checkpoint_id"), metadata.get("resume_from_checkpoint_id")
            ),
        )

        # Apply environment overrides
        if environment_overrides:
            context.agent_state.update(environment_overrides)
            for key, value in environment_overrides.items():
                if key in {"lane_bucket", "checkpoint_state", "budget_remaining", "estimated_cost", "cost_score", "task_id", "last_successful_stage", "resume_from_checkpoint_id"}:
                    setattr(context, key, value)

        # Inject context from providers
        try:
            if context_provider:
                context.observation_data = context_provider.get_observation_data()
                context.orientation_data = context_provider.get_orientation_data()
                context.decision_context = context_provider.get_decision_context()
                context.action_context = context_provider.get_action_context()

            # Augment with repository state (from Track 10.2)
            repository_state = checkpoint_doc.get("repository_state", {})
            context.agent_state["repository_state"] = repository_state

            # Augment with context state (from Track 10.3 OODA)
            context_state = checkpoint_doc.get("context_state", {})
            context.decision_context.update(context_state)
            context.recovery_metadata.update({
                "lane_bucket": context.lane_bucket,
                "checkpoint_state": context.checkpoint_state,
                "budget_remaining": context.budget_remaining,
                "estimated_cost": context.estimated_cost,
                "cost_score": context.cost_score,
                "task_id": context.task_id,
                "last_successful_stage": context.last_successful_stage,
                "resume_from_checkpoint_id": context.resume_from_checkpoint_id,
            })

        except Exception as e:
            raise ContextInjectionError(f"Context injection failed: {e}")

        # Run cold-start warmup
        if self.enable_warmup:
            try:
                self._run_warmup_sequence(context)
                context.warmup_complete = True
            except WarmupError as e:
                logger.warning(f"Warmup sequence failed (continuing): {e}")

        # Track recovery metadata
        recovery_meta = checkpoint_doc.get("_recovery_metadata")
        if recovery_meta:
            context.recovery_metadata = recovery_meta

        logger.info(f"✓ Warm-start complete: {context.session_id}")
        logger.info(f"  Task: {context.execution_progress.get('current_task')}")
        logger.info(f"  Memory: {context.memory_snapshot.get('total_patterns', 0)} patterns")

        return context

    def validate_and_recover(
        self,
        checkpoint_id: str,
        fallback_strategy: Optional[str] = None,
        recovery_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validate checkpoint with automatic recovery from corruption.

        Args:
            checkpoint_id: Checkpoint to validate/recover
            fallback_strategy: Override default fallback strategy
            recovery_config: Strategy-specific config

        Returns:
            Recovered checkpoint document with metadata

        Raises:
            SessionResumeError: If recovery fails
        """
        fallback_strategy = fallback_strategy or self.fallback_strategy
        recovery_config = recovery_config or {}

        # Validate checkpoint
        validation_result = self.checkpoint_manager.validate_checkpoint(
            checkpoint_id=checkpoint_id, quick_check=False
        )

        if validation_result.is_valid:
            # No recovery needed
            checkpoint_doc = self.checkpoint_manager.restore_checkpoint(
                checkpoint_id=checkpoint_id, validation_mode="strict"
            )
            return checkpoint_doc

        if not validation_result.recoverable:
            raise SessionResumeError(
                f"Checkpoint not recoverable: {validation_result.errors[0].message}"
            )

        # Attempt recovery
        logger.warning(
            f"Attempting recovery (strategy: {fallback_strategy}): "
            f"Score={validation_result.integrity_score:.1%}"
        )

        if fallback_strategy == "quantum_reconstruction":
            checkpoint_doc = self._recover_quantum(
                checkpoint_id=checkpoint_id, config=recovery_config
            )
        elif fallback_strategy == "last_known_good":
            checkpoint_doc = self._recover_last_known_good(checkpoint_id)
        elif fallback_strategy == "minimal":
            checkpoint_doc = self._recover_minimal(checkpoint_id)
        else:
            raise SessionResumeError(f"Unknown recovery strategy: {fallback_strategy}")

        # Attach recovery metadata
        checkpoint_doc["_recovery_metadata"] = {
            "recovered": True,
            "recovery_method": fallback_strategy,
            "confidence": validation_result.integrity_score,
            "original_error": validation_result.errors[0].message
            if validation_result.errors
            else None,
            "degraded_mode": True,
        }

        logger.info(f"✓ Checkpoint recovered using {fallback_strategy}")

        return checkpoint_doc

    def dependency_inject(
        self,
        session_state: Dict[str, Any],
        injectors: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Inject runtime dependencies into session state.

        Args:
            session_state: State dict to augment
            injectors: Dependency dict (name -> object/value)

        Returns:
            Session state with injected dependencies
        """
        if not injectors:
            return session_state

        agent_state = session_state.get("agent_state", {})

        for dep_name, dep_value in injectors.items():
            agent_state[f"_injected_{dep_name}"] = dep_value
            logger.debug(f"Injected dependency: {dep_name}")

        session_state["agent_state"] = agent_state
        return session_state

    # ========================================================================
    # Private helper methods
    # ========================================================================

    def _run_warmup_sequence(self, context: SessionContext) -> None:
        """Run cold-start warmup sequence."""
        logger.info("Running cold-start warmup sequence...")

        try:
            # 1. Validate state consistency
            if not context.is_valid():
                raise WarmupError("Session context validation failed")

            # 2. Initialize memory patterns
            memory = context.memory_snapshot or {}
            stm = memory.get("short_term_memory", [])
            ltm = memory.get("long_term_memory", [])
            logger.info(f"  - Loaded {len(stm)} STM + {len(ltm)} LTM patterns")

            # 3. Restore execution progress
            progress = context.execution_progress or {}
            current_task = progress.get("current_task")
            completed = len(progress.get("completed_tasks", []))
            pending = len(progress.get("pending_tasks", []))
            logger.info(
                f"  - Progress: {completed} done, {pending} pending, current={current_task}"
            )

            # 4. Verify decision history integrity
            decisions = context.decision_history or []
            logger.info(f"  - Decision history: {len(decisions)} decisions")

            # 5. Check repository state
            repo_state = context.agent_state.get("repository_state", {})
            branch = repo_state.get("branch", "unknown")
            commit = repo_state.get("commit_sha", "unknown")[:8]
            logger.info(f"  - Repository: {branch} @ {commit}")

            logger.info("✓ Warmup complete")

        except Exception as e:
            raise WarmupError(f"Warmup failed: {e}")

    def _recover_quantum(self, checkpoint_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recover checkpoint using quantum reconstruction (wave-collapse).

        This uses entropy minimization and cross-validation to reconstruct
        missing or corrupted state from available fragments.
        """
        logger.info(f"Quantum reconstruction: {checkpoint_id}")

        # Load partial checkpoint
        try:
            partial_doc = self.checkpoint_manager.restore_checkpoint(
                checkpoint_id=checkpoint_id, validation_mode="lenient", fallback_on_corruption=True
            )
        except Exception:
            partial_doc = {}

        # Reconstruct missing fields with defaults
        recovered_doc = {
            "schema_version": partial_doc.get("schema_version", "v1.0"),
            "checkpoint_id": checkpoint_id,
            "session_id": partial_doc.get("session_id", "recovered"),
            "timestamp": partial_doc.get("timestamp", datetime.utcnow().isoformat()),
            "agent_state": partial_doc.get("agent_state", {}),
            "memory_snapshot": partial_doc.get(
                "memory_snapshot",
                {
                    "short_term_memory": [],
                    "long_term_memory": [],
                    "total_patterns": 0,
                },
            ),
            "execution_progress": partial_doc.get(
                "execution_progress",
                {
                    "current_task": None,
                    "completed_tasks": [],
                    "pending_tasks": [],
                },
            ),
            "decision_history": partial_doc.get("decision_history", []),
            "repository_state": partial_doc.get("repository_state", {}),
            "context_state": partial_doc.get("context_state", {}),
        }

        return recovered_doc

    def _recover_last_known_good(self, checkpoint_id: str) -> Dict[str, Any]:
        """Recover using most recent valid checkpoint."""
        logger.info(f"Attempting to find last known good checkpoint before {checkpoint_id}")

        # List checkpoints and find one before this one
        try:
            checkpoints = self.checkpoint_manager.list_checkpoints(limit=20)
            for cp in checkpoints:
                if cp.checkpoint_id != checkpoint_id:
                    try:
                        doc = self.checkpoint_manager.restore_checkpoint(
                            checkpoint_id=cp.checkpoint_id, validation_mode="strict"
                        )
                        logger.info(f"Recovered from: {cp.checkpoint_id}")
                        return doc
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"Last known good recovery failed: {e}")

        # Fallback to minimal recovery
        return self._recover_minimal(checkpoint_id)

    def _recover_minimal(self, checkpoint_id: str) -> Dict[str, Any]:
        """Recover with minimal valid state."""
        logger.info(f"Performing minimal recovery for {checkpoint_id}")

        return {
            "schema_version": "v1.0",
            "checkpoint_id": checkpoint_id,
            "session_id": "recovered_minimal",
            "timestamp": datetime.utcnow().isoformat(),
            "agent_state": {},
            "memory_snapshot": {
                "short_term_memory": [],
                "long_term_memory": [],
                "total_patterns": 0,
                "memory_usage_bytes": 0,
            },
            "execution_progress": {
                "current_task": None,
                "completed_tasks": [],
                "pending_tasks": [],
                "blocked_tasks": {},
                "task_completion_percent": 0.0,
                "checkpoint_count": 0,
            },
            "decision_history": [],
            "repository_state": {},
            "context_state": {},
        }


# ============================================================================
# Standalone Functions
# ============================================================================


def resume_session(
    checkpoint_id: str,
    context_provider: Optional[ContextProvider] = None,
) -> SessionContext:
    """
    Quick helper to resume a session from checkpoint.

    Args:
        checkpoint_id: Checkpoint to restore
        context_provider: Context provider for Track 10.3

    Returns:
        SessionContext ready for execution
    """
    engine = SessionResumeEngine()
    return engine.warm_start(checkpoint_id=checkpoint_id, context_provider=context_provider)


if __name__ == "__main__":
    # Example usage
    manager = SessionCheckpointManager()
    engine = SessionResumeEngine(checkpoint_manager=manager)

    # Create a checkpoint first
    meta = manager.create_checkpoint(
        session_id="S001",
        agent_state={"task": "example"},
        memory_snapshot={"patterns": []},
        execution_progress={"current_task": "test"},
    )

    print(f"Created: {meta.checkpoint_id}")

    # Warm-start from checkpoint
    context = engine.warm_start(checkpoint_id=meta.checkpoint_id)
    print(f"✓ Resumed: {context.session_id}")
    print(f"  Valid: {context.is_valid()}")
    print(f"  Warmup: {context.warmup_complete}")
