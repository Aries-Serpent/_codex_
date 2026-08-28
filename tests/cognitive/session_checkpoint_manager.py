"""Local test shims for checkpoint manager imports.

These files satisfy the project's legacy module layout used by
``tests/cognitive/test_session_checkpoint.py`` while the canonical implementation
still lives under ``scripts/cognitive``.
"""

from scripts.cognitive.session_checkpoint_manager import *  # noqa: F401,F403
from scripts.cognitive.session_checkpoint_manager import __all__ as _checkpoint_all

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
