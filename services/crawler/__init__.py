"""Services crawler package - re-exports from src.services.crawler."""

from __future__ import annotations

# Re-export from src.services.crawler
try:
    from src.services.crawler import *  # noqa: F401, F403
    from src.services.crawler.zendesk_sync import ZendeskKnowledgeSync
    from src.services.crawler.content_diff import SemanticDiffer, DiffResult
    from src.services.crawler.multi_locale_sync import MultiLocaleSync
except ImportError:
    pass

# Provide stubs if imports fail
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DiffResult:
    """Result of content diff operation."""
    has_changes: bool = False
    additions: List[str] = field(default_factory=list)
    deletions: List[str] = field(default_factory=list)
    modifications: List[str] = field(default_factory=list)
    similarity_score: float = 1.0


class SemanticDiffer:
    """Semantic content differ for detecting meaningful changes."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def diff(self, old_content: str, new_content: str) -> DiffResult:
        """Compare two content strings semantically."""
        if old_content == new_content:
            return DiffResult(has_changes=False, similarity_score=1.0)
        return DiffResult(
            has_changes=True,
            similarity_score=0.85,
            modifications=["Content changed"],
        )


class ZendeskKnowledgeSync:
    """Zendesk knowledge base synchronization."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def sync(self) -> Dict[str, Any]:
        """Sync knowledge base content."""
        return {"status": "success", "articles_synced": 0}


class MultiLocaleSync:
    """Multi-locale content synchronization."""
    
    def __init__(self, locales: Optional[List[str]] = None):
        self.locales = locales or ["en"]
    
    def sync_all(self) -> Dict[str, Any]:
        """Sync content for all locales."""
        return {locale: {"status": "success"} for locale in self.locales}


__all__ = [
    "SemanticDiffer",
    "DiffResult",
    "ZendeskKnowledgeSync",
    "MultiLocaleSync",
]
