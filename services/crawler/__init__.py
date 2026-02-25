"""Services crawler package."""

from __future__ import annotations

# Import from local content_diff module
from .content_diff import (
    ChangeType,
    ContentDiffer,
    ContentDiffResult,
    DiffSegment,
    IncrementalSyncDecider,
    SemanticDiffer,
)

# For backwards compatibility, alias ContentDiffResult as DiffResult
DiffResult = ContentDiffResult

__all__ = [
    "SemanticDiffer",
    "ContentDiffResult",
    "DiffResult",
    "ChangeType",
    "ContentDiffer",
    "IncrementalSyncDecider",
    "DiffSegment",
]
