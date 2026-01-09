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
    from src.services.crawler.zendesk_sync import ZendeskKnowledgeSyncService

try:
    from services.crawler.multi_locale_sync import MultiLocaleSyncManager, LocaleConfig
except ImportError:
    from src.services.crawler.multi_locale_sync import MultiLocaleSyncManager, LocaleConfig

try:
    from services.crawler.content_diff import ContentDiffer, IncrementalSyncDecider
except ImportError:
    from src.services.crawler.content_diff import ContentDiffer, IncrementalSyncDecider
