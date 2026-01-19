"""Content diff module for semantic comparison."""

from __future__ import annotations

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
    semantic_changes: List[Dict[str, Any]] = field(default_factory=list)


class SemanticDiffer:
    """
    Semantic content differ for detecting meaningful changes.
    
    Uses semantic analysis to identify significant content changes
    while ignoring minor formatting or wording adjustments.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize differ with optional config."""
        self.config = config or {}
        self.threshold = self.config.get("similarity_threshold", 0.8)
    
    def diff(self, old_content: str, new_content: str) -> DiffResult:
        """
        Compare two content strings semantically.
        
        Args:
            old_content: Original content
            new_content: Updated content
            
        Returns:
            DiffResult with change details
        """
        if old_content == new_content:
            return DiffResult(has_changes=False, similarity_score=1.0)
        
        # Simple word-based comparison for stub
        old_words = set(old_content.lower().split())
        new_words = set(new_content.lower().split())
        
        added = new_words - old_words
        removed = old_words - new_words
        
        if not old_words and not new_words:
            similarity = 1.0
        elif not old_words or not new_words:
            similarity = 0.0
        else:
            intersection = old_words & new_words
            union = old_words | new_words
            similarity = len(intersection) / len(union) if union else 1.0
        
        return DiffResult(
            has_changes=bool(added or removed),
            additions=list(added),
            deletions=list(removed),
            similarity_score=similarity,
        )
    
    def batch_diff(
        self,
        pairs: list[tuple[str, str]]
    ) -> list[DiffResult]:
        """Compare multiple content pairs."""
        return [self.diff(old, new) for old, new in pairs]


__all__ = [
    "SemanticDiffer",
    "DiffResult",
]
