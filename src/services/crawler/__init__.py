"""Knowledge synchronization crawler services.

This module provides services to synchronize Agent knowledge bases
with SaaS Knowledge Centers using a "Check and Pull" mechanism.
"""

from __future__ import annotations

__all__ = ["ZendeskKnowledgeSyncService"]

from src.services.crawler.zendesk_sync import ZendeskKnowledgeSyncService
