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


class MultiLocaleSyncManager:
    """Manager for multi-locale content synchronization."""
    def __init__(self):
        self.locales = {}
    
    def sync_locale(self, locale, content):
        """Synchronize content for a specific locale."""
        self.locales[locale] = content
        return True


__all__ = [
    "SemanticDiffer",
    "ContentDiffResult",
    "DiffResult",
    "ChangeType",
    "ContentDiffer",
    "IncrementalSyncDecider",
    "DiffSegment",
    "MultiLocaleSyncManager",
]
