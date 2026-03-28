"""Knowledge synchronization crawler services.

This module provides services to synchronize Agent knowledge bases
with SaaS Knowledge Centers using a "Check and Pull" mechanism.

PS-06 Enhancement: Includes multi-locale sync and content diffing.
"""

from __future__ import annotations

__all__ = [
    "ZendeskKnowledgeSyncService",
    "MultiLocaleSyncManager",
    "LocaleConfig",
    "ContentDiffer",
    "IncrementalSyncDecider",
]

try:
    from services.crawler.zendesk_sync import ZendeskKnowledgeSyncService
except ImportError:
    from services.crawler.zendesk_sync import ZendeskKnowledgeSyncService  # type: ignore[no-redef]

try:
    from services.crawler.multi_locale_sync import (
        LocaleConfig,
        MultiLocaleSyncManager,
    )
except ImportError:
    from services.crawler.multi_locale_sync import (  # type: ignore[assignment]
        LocaleConfig,
        MultiLocaleSyncManager,
    )

try:
    from services.crawler.content_diff import ContentDiffer, IncrementalSyncDecider
except ImportError:
    from services.crawler.content_diff import (  # type: ignore[assignment]
        ContentDiffer,
        IncrementalSyncDecider,
    )
