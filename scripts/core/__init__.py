"""
Core Autonomy Foundations

Systems for deterministic execution loops:
- validation_engine: Post-action constraint verification
- checkpoint_manager: State persistence and recovery
- handoff_protocol: Agent-to-agent context transfer
"""

from .checkpoint_manager import (
    CheckpointManager,
    create_checkpoint,
    load_checkpoint,
    resume_execution,
)
from .handoff_protocol import (
    HandoffObject,
    HandoffProtocol,
    prepare_handoff,
    resume_from_handoff,
    validate_handoff,
)
from .validation_engine import (
    ValidationRule,
    ValidatorConfig,
    validate_state,
    validate_state_transition,
)

__all__ = [
    "validate_state",
    "validate_state_transition",
    "ValidationRule",
    "ValidatorConfig",
    "CheckpointManager",
    "create_checkpoint",
    "load_checkpoint",
    "resume_execution",
    "HandoffProtocol",
    "HandoffObject",
    "prepare_handoff",
    "resume_from_handoff",
    "validate_handoff"
]
