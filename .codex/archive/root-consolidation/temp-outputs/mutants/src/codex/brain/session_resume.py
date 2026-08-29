"""Session Resume — Restores agent sessions from checkpoints.

Phase 10.1 Implementation: Complete session recovery and state restoration
from saved checkpoints.

Responsibilities:
- Validate checkpoint integrity (SHA256)
- Load serialized state from disk
- Restore agent state (ID, memory, decisions)
- Reconcile repository state (check for divergence)
- Support schema version compatibility
- Prevent work duplication via progress tracking
- Graceful degradation on errors

Recovery Workflow:
1. **Validate** — Verify checkpoint integrity (SHA256)
2. **Load** — Deserialize state from disk
3. **Restore** — Inject state into agent
4. **Reconcile** — Check repository state hasn't diverged
5. **Resume** — Continue from last task

Usage:
    from codex.brain.session_resume import SessionResume
    from codex.brain.checkpoint_manager import CheckpointManager

    checkpoint_mgr = CheckpointManager()
    resume_mgr = SessionResume(checkpoint_mgr)

    # Validate checkpoint
    if resume_mgr.validate_checkpoint("cp_20260701_001"):
        # Load and restore session
        agent_state = resume_mgr.resume_session("cp_20260701_001")
        logger.info(f"Resumed session: {agent_state}")
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from codex.brain.checkpoint_manager import CheckpointManager
from codex.brain.session_serializer import SessionSerializer
from codex.logging.structured_logger import logger


@dataclass
class ResumeResult:
    """Result of session resume operation."""

    success: bool
    checkpoint_id: str
    agent_id: str
    session_id: str
    state: dict[str, Any]
    error_message: Optional[str] = None
    warnings: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []


@dataclass
class RepositoryDivergence:
    """Represents repository state divergence."""

    diverged: bool
    current_branch: str
    checkpoint_branch: str
    current_commit: str
    checkpoint_commit: str
    uncommitted_changes: int
    conflicts: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.conflicts is None:
            self.conflicts = []


class SessionResume:
    """Manages session recovery from checkpoints."""

    RESUME_VERSION = "1.0.0"
    SUPPORTED_SCHEMA_VERSIONS = [1]  # Support multiple schema versions

    def __init__(self, checkpoint_manager: CheckpointManager):
        """Initialize SessionResume.

        Args:
            checkpoint_manager: CheckpointManager instance
        """
        self.checkpoint_manager = checkpoint_manager
        self.serializer = SessionSerializer()
        logger.info(f"SessionResume initialized: version={self.RESUME_VERSION}")

    def validate_checkpoint(self, checkpoint_id: str) -> bool:
        """Validate checkpoint integrity.

        Args:
            checkpoint_id: ID of checkpoint to validate

        Returns:
            True if checkpoint is valid, False otherwise
        """
        logger.info(f"Validating checkpoint: {checkpoint_id}")

        # Check if checkpoint exists
        if not self.checkpoint_manager.verify_checkpoint_integrity(checkpoint_id):
            logger.error(f"Checkpoint failed integrity check: {checkpoint_id}")
            return False

        # Load and validate content
        content = self.checkpoint_manager.get_checkpoint_content(checkpoint_id)
        if not content:
            logger.error(f"Failed to load checkpoint content: {checkpoint_id}")
            return False

        # Validate schema version
        schema_version = content.get("schema_version")
        if schema_version not in self.SUPPORTED_SCHEMA_VERSIONS:
            logger.error(
                f"Checkpoint schema version {schema_version} not supported "
                f"(supported: {self.SUPPORTED_SCHEMA_VERSIONS})"
            )
            return False

        logger.info(f"Checkpoint validation successful: {checkpoint_id}")
        return True

    def load_checkpoint(self, checkpoint_id: str) -> Optional[dict[str, Any]]:
        """Load checkpoint content.

        Args:
            checkpoint_id: ID of checkpoint to load

        Returns:
            Checkpoint content dict or None on error
        """
        logger.info(f"Loading checkpoint: {checkpoint_id}")

        if not self.validate_checkpoint(checkpoint_id):
            return None

        content = self.checkpoint_manager.get_checkpoint_content(checkpoint_id)
        if content:
            logger.info(f"Checkpoint loaded successfully: {checkpoint_id}")
        else:
            logger.error(f"Failed to load checkpoint: {checkpoint_id}")

        return content

    def resume_session(
        self, checkpoint_id: str, current_repository_state: Optional[dict[str, Any]] = None
    ) -> Optional[ResumeResult]:
        """Resume session from checkpoint.

        Complete recovery workflow:
        1. Validate checkpoint
        2. Load serialized state
        3. Restore agent state
        4. Reconcile repository state
        5. Return recovery result

        Args:
            checkpoint_id: ID of checkpoint to resume from
            current_repository_state: Current repository state dict (optional)

        Returns:
            ResumeResult or None on error
        """
        logger.info(f"Resuming session from checkpoint: {checkpoint_id}")

        # Step 1: Validate checkpoint
        if not self.validate_checkpoint(checkpoint_id):
            return ResumeResult(
                success=False,
                checkpoint_id=checkpoint_id,
                agent_id="unknown",
                session_id="unknown",
                state={},
                error_message=f"Checkpoint validation failed: {checkpoint_id}",
            )

        # Step 2: Load checkpoint content
        content = self.load_checkpoint(checkpoint_id)
        if not content:
            return ResumeResult(
                success=False,
                checkpoint_id=checkpoint_id,
                agent_id="unknown",
                session_id="unknown",
                state={},
                error_message=f"Failed to load checkpoint content: {checkpoint_id}",
            )

        # Extract key information
        agent_id = content.get("agent_id", "unknown")
        session_id = content.get("session_id", "unknown")
        content.get("session_state", {})

        logger.info(f"Checkpoint content loaded: agent_id={agent_id}, session_id={session_id}")

        # Step 3: Restore agent state
        restored_state = self._restore_agent_state(content)
        if not restored_state:
            return ResumeResult(
                success=False,
                checkpoint_id=checkpoint_id,
                agent_id=agent_id,
                session_id=session_id,
                state={},
                error_message="Failed to restore agent state from checkpoint",
            )

        # Step 4: Reconcile repository state
        warnings = []
        if current_repository_state:
            divergence = self._check_repository_divergence(content, current_repository_state)
            if divergence.diverged:
                warning = f"Repository state divergence detected: {divergence}"
                warnings.append(warning)
                logger.warning(warning)

        # Step 5: Return recovery result
        logger.info(f"Session resumed successfully: {session_id}")
        return ResumeResult(
            success=True,
            checkpoint_id=checkpoint_id,
            agent_id=agent_id,
            session_id=session_id,
            state=restored_state,
            warnings=warnings,
        )

    def resume_latest_session(
        self, current_repository_state: Optional[dict[str, Any]] = None
    ) -> Optional[ResumeResult]:
        """Resume from the most recent checkpoint.

        Args:
            current_repository_state: Current repository state dict (optional)

        Returns:
            ResumeResult or None if no checkpoints available
        """
        latest_checkpoint = self.checkpoint_manager.get_latest_checkpoint()
        if not latest_checkpoint:
            logger.warning("No checkpoints available for resume")
            return None

        logger.info(f"Resuming from latest checkpoint: {latest_checkpoint}")
        return self.resume_session(latest_checkpoint, current_repository_state)

    def get_progress_snapshot(self, checkpoint_id: str) -> Optional[dict[str, Any]]:
        """Get execution progress from checkpoint.

        Args:
            checkpoint_id: ID of checkpoint

        Returns:
            Progress dict or None
        """
        content = self.load_checkpoint(checkpoint_id)
        if not content:
            return None

        session_state = content.get("session_state", {})
        execution_progress = session_state.get("execution_progress", {})

        return {
            "current_task": execution_progress.get("current_task"),
            "completed_tasks": execution_progress.get("completed_tasks", []),
            "pending_tasks": execution_progress.get("pending_tasks", []),
            "failed_tasks": execution_progress.get("failed_tasks", []),
            "work_items": execution_progress.get(
                "work_items", {"total": 0, "completed": 0, "failed": 0, "pending": 0}
            ),
            "milestones": execution_progress.get(
                "milestones", {"completed": [], "current": None, "pending": []}
            ),
        }

    def get_decision_history(self, checkpoint_id: str) -> Optional[list[dict[str, Any]]]:
        """Get decision history from checkpoint.

        Args:
            checkpoint_id: ID of checkpoint

        Returns:
            List of decision dicts or None
        """
        content = self.load_checkpoint(checkpoint_id)
        if not content:
            return None

        session_state = content.get("session_state", {})
        return session_state.get("decision_history", [])

    # Private Methods

    def _restore_agent_state(self, checkpoint_content: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Restore agent state from checkpoint.

        Args:
            checkpoint_content: Checkpoint content dict

        Returns:
            Restored agent state dict or None on error
        """
        try:
            session_state = checkpoint_content.get("session_state", {})

            restored_state = {
                "agent_id": checkpoint_content.get("agent_id"),
                "session_id": checkpoint_content.get("session_id"),
                "timestamp_resumed": checkpoint_content.get("timestamp"),
                "agent_state": session_state.get("agent_state", {}),
                "decision_history": session_state.get("decision_history", []),
                "memory_snapshot": session_state.get("memory_snapshot", {}),
                "execution_progress": session_state.get("execution_progress", {}),
                "context_snapshot": session_state.get("context_snapshot", {}),
            }

            logger.info("Agent state restored successfully")
            return restored_state

        except Exception as e:
            logger.error(f"Failed to restore agent state: {e}")
            return None

    def _check_repository_divergence(
        self, checkpoint_content: dict[str, Any], current_repository_state: dict[str, Any]
    ) -> RepositoryDivergence:
        """Check if repository state has diverged since checkpoint.

        Args:
            checkpoint_content: Checkpoint content dict
            current_repository_state: Current repository state dict

        Returns:
            RepositoryDivergence object
        """
        session_state = checkpoint_content.get("session_state", {})
        checkpoint_repo_state = session_state.get("repository_state", {})

        checkpoint_branch = checkpoint_repo_state.get("branch", "unknown")
        checkpoint_commit = checkpoint_repo_state.get("commit_sha", "unknown")

        current_branch = current_repository_state.get("branch", "unknown")
        current_commit = current_repository_state.get("commit_sha", "unknown")
        current_uncommitted = current_repository_state.get("uncommitted_changes", 0)

        diverged = checkpoint_branch != current_branch or checkpoint_commit != current_commit

        if diverged:
            logger.warning(
                f"Repository divergence detected: "
                f"branch {checkpoint_branch} -> {current_branch}, "
                f"commit {checkpoint_commit[:8]} -> {current_commit[:8]}"
            )

        return RepositoryDivergence(
            diverged=diverged,
            current_branch=current_branch,
            checkpoint_branch=checkpoint_branch,
            current_commit=current_commit,
            checkpoint_commit=checkpoint_commit,
            uncommitted_changes=current_uncommitted,
        )

    def _validate_schema_compatibility(self, schema_version: int) -> bool:
        """Check if schema version is supported.

        Args:
            schema_version: Schema version from checkpoint

        Returns:
            True if compatible, False otherwise
        """
        if schema_version in self.SUPPORTED_SCHEMA_VERSIONS:
            return True

        logger.error(
            f"Schema version {schema_version} not supported "
            f"(supported: {self.SUPPORTED_SCHEMA_VERSIONS})"
        )
        return False

    def _apply_schema_migration(
        self, state_dict: dict[str, Any], from_version: int, to_version: int
    ) -> dict[str, Any]:
        """Apply schema migrations if needed.

        Args:
            state_dict: State dictionary
            from_version: Source schema version
            to_version: Target schema version

        Returns:
            Migrated state dictionary
        """
        # Currently only v1 is supported, so no migrations needed
        if from_version == to_version:
            return state_dict

        logger.warning(
            f"Schema migration needed: {from_version} -> {to_version} (not yet implemented)"
        )
        return state_dict
