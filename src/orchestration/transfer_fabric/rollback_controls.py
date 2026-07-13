"""Rollback Controls: Atomic state restoration and checkpoint management.

Provides atomic rollback to restore pre-transfer state, with checkpoint
system for safe recovery.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class Checkpoint:
    """Saved checkpoint of system state."""

    checkpoint_id: str = field(default_factory=lambda: str(uuid4()))
    transfer_id: str = ""
    state_data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "transfer_id": self.transfer_id,
            "state_data": self.state_data,
            "created_at": self.created_at,
            "valid": self.valid,
        }


@dataclass
class RollbackResult:
    """Result of rollback operation."""

    success: bool
    time_ms: int = 0
    data_restored: int = 0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "time_ms": self.time_ms,
            "data_restored": self.data_restored,
            "error_message": self.error_message,
        }


class RollbackManager:
    """Manages atomic rollback and checkpoint system."""

    def __init__(self):
        """Initialize rollback manager."""
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.transfer_checkpoints: Dict[str, str] = {}
        self.restored_states: Dict[str, Dict[str, Any]] = {}

    def create_checkpoint(
        self, transfer_id: str, state_data: Dict[str, Any]
    ) -> Checkpoint:
        """Create a checkpoint before transfer."""
        checkpoint = Checkpoint(
            transfer_id=transfer_id,
            state_data=state_data.copy(),
        )
        self.checkpoints[checkpoint.checkpoint_id] = checkpoint
        self.transfer_checkpoints[transfer_id] = checkpoint.checkpoint_id

        logger.info(
            f"Checkpoint created: {checkpoint.checkpoint_id} for transfer {transfer_id}"
        )
        return checkpoint

    def validate_checkpoint(self, checkpoint_id: str) -> bool:
        """Validate checkpoint integrity."""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if not checkpoint:
            return False

        if not checkpoint.state_data:
            return False

        return checkpoint.valid

    def rollback_to_checkpoint(self, checkpoint_id: str) -> RollbackResult:
        """Atomically rollback to a checkpoint."""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if not checkpoint:
            return RollbackResult(
                success=False,
                error_message=f"Checkpoint not found: {checkpoint_id}",
            )

        if not self.validate_checkpoint(checkpoint_id):
            return RollbackResult(
                success=False,
                error_message=f"Checkpoint invalid: {checkpoint_id}",
            )

        start_time = datetime.now(timezone.utc)
        state_bytes = sum(
            len(str(v).encode()) for v in checkpoint.state_data.values()
        )

        self.restored_states[checkpoint_id] = checkpoint.state_data.copy()

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        logger.info(f"Rollback complete: {checkpoint_id}, {state_bytes} bytes restored")

        return RollbackResult(
            success=True,
            time_ms=int(elapsed),
            data_restored=state_bytes,
        )

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Get checkpoint by ID."""
        return self.checkpoints.get(checkpoint_id)

    def get_transfer_checkpoint(self, transfer_id: str) -> Optional[Checkpoint]:
        """Get checkpoint for a transfer."""
        checkpoint_id = self.transfer_checkpoints.get(transfer_id)
        if checkpoint_id:
            return self.checkpoints.get(checkpoint_id)
        return None

    def invalidate_checkpoint(self, checkpoint_id: str) -> None:
        """Mark checkpoint as invalid."""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if checkpoint:
            checkpoint.valid = False
            logger.info(f"Checkpoint invalidated: {checkpoint_id}")

    def cascade_rollback(self, transfer_ids: list) -> Dict[str, RollbackResult]:
        """Perform cascading rollback for multiple transfers."""
        results = {}

        for transfer_id in transfer_ids:
            checkpoint_id = self.transfer_checkpoints.get(transfer_id)
            if checkpoint_id:
                result = self.rollback_to_checkpoint(checkpoint_id)
                results[transfer_id] = result
            else:
                results[transfer_id] = RollbackResult(
                    success=False,
                    error_message=f"No checkpoint for transfer: {transfer_id}",
                )

        logger.info(f"Cascade rollback completed: {len(results)} transfers")
        return results

    def cleanup_checkpoints(self, transfer_id: str) -> int:
        """Clean up checkpoints for a transfer."""
        checkpoint_id = self.transfer_checkpoints.get(transfer_id)
        if not checkpoint_id:
            return 0

        if checkpoint_id in self.checkpoints:
            del self.checkpoints[checkpoint_id]
        if transfer_id in self.transfer_checkpoints:
            del self.transfer_checkpoints[transfer_id]
        if checkpoint_id in self.restored_states:
            del self.restored_states[checkpoint_id]

        logger.info(f"Checkpoints cleaned up for transfer: {transfer_id}")
        return 1

    def get_restore_state(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get the restored state from a rollback."""
        return self.restored_states.get(checkpoint_id)

    def checkpoint_exists(self, checkpoint_id: str) -> bool:
        """Check if checkpoint exists."""
        return checkpoint_id in self.checkpoints
