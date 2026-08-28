"""Compatibility wrapper for legacy ``cognitive`` imports.

This module intentionally re-exports the canonical implementation living under
``scripts.cognitive`` so older tests and tooling still resolve the same APIs.
"""

from scripts.cognitive.session_checkpoint_manager import *  # noqa: F401,F403

try:
    from scripts.cognitive.session_checkpoint_manager import __all__ as _checkpoint_all
except ImportError:
    _checkpoint_all = None

__all__ = list(_checkpoint_all) if isinstance(_checkpoint_all, list) else [
    "SessionCheckpointManager",
    "CheckpointNotFoundError",
    "CheckpointCorruptedError",
    "CompressionError",
    "StorageError",
    "ValidationFailedError",
    "CheckpointMetadata",
    "DeletionResult",
    "ValidationResult",
    "ValidationError",
]
