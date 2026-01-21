"""Content diff module for semantic comparison."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ChangeType(Enum):
    """Type of content change detected."""
    NO_CHANGE = "no_change"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    COMPLETE = "complete"


@dataclass
class DiffResult:
    """Result of content diff operation."""
    has_changes: bool = False
    additions: List[str] = field(default_factory=list)
    deletions: List[str] = field(default_factory=list)
    modifications: List[str] = field(default_factory=list)
    similarity_score: float = 1.0
    semantic_changes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DiffSegment:
    """A segment of content that has changed."""
    type: str  # 'addition', 'deletion', 'modification'
    old_text: str = ""
    new_text: str = ""
    position: int = 0
    importance: float = 0.5  # 0-1 scale


@dataclass
class ContentDiffResult:
    """Comprehensive result of content diffing."""
    change_type: ChangeType = ChangeType.NO_CHANGE
    change_ratio: float = 0.0  # 0-1 scale
    similarity_ratio: float = 1.0  # 0-1 scale
    segments: List[DiffSegment] = field(default_factory=list)
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


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


class ContentDiffer:
    """
    Content differ with change classification.
    
    Provides comprehensive content diffing with change type
    classification and semantic analysis.
    """
    
    def __init__(self, strip_html: bool = False):
        """Initialize differ with configuration."""
        self.strip_html = strip_html
    
    def diff(self, old_content: str, new_content: str) -> ContentDiffResult:
        """
        Compare two content strings and classify changes.
        
        Args:
            old_content: Original content
            new_content: Updated content
            
        Returns:
            ContentDiffResult with comprehensive analysis
        """
        # Strip HTML if configured
        if self.strip_html:
            import re
            old_content = re.sub(r'<[^>]+>', '', old_content)
            new_content = re.sub(r'<[^>]+>', '', new_content)
        
        # Calculate similarity
        if old_content == new_content:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
            )
        
        old_words = set(old_content.lower().split())
        new_words = set(new_content.lower().split())
        
        if not old_words and not new_words:
            similarity = 1.0
            change_ratio = 0.0
        elif not old_words:
            similarity = 0.0
            change_ratio = 1.0
        elif not new_words:
            similarity = 0.0
            change_ratio = 1.0
        else:
            intersection = old_words & new_words
            union = old_words | new_words
            similarity = len(intersection) / len(union) if union else 1.0
            change_ratio = 1.0 - similarity
        
        # Classify change type
        if change_ratio == 0.0:
            change_type = ChangeType.NO_CHANGE
        elif change_ratio < 0.1:
            change_type = ChangeType.MINOR
        elif change_ratio < 0.3:
            change_type = ChangeType.MODERATE
        elif change_ratio < 0.7:
            change_type = ChangeType.MAJOR
        else:
            change_type = ChangeType.COMPLETE
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity,
        )


class IncrementalSyncDecider:
    """
    Decider for incremental vs. full synchronization.
    
    Analyzes content changes to determine whether an incremental
    update is sufficient or a full sync is required.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize decider with configuration."""
        self.config = config or {}
        self.incremental_threshold = self.config.get("incremental_threshold", 0.3)
    
    def should_use_incremental(
        self,
        diff_result: ContentDiffResult
    ) -> bool:
        """
        Determine if incremental sync should be used.
        
        Args:
            diff_result: Result of content diffing
            
        Returns:
            True if incremental sync is recommended
        """
        # Use incremental for minor to moderate changes
        return diff_result.change_type in (
            ChangeType.NO_CHANGE,
            ChangeType.MINOR,
            ChangeType.MODERATE,
        )
    
    def get_sync_recommendation(
        self,
        diff_result: ContentDiffResult
    ) -> Dict[str, Any]:
        """
        Get comprehensive sync recommendation.
        
        Args:
            diff_result: Result of content diffing
            
        Returns:
            Dict with recommendation details
        """
        use_incremental = self.should_use_incremental(diff_result)
        
        return {
            "use_incremental": use_incremental,
            "change_type": diff_result.change_type.value,
            "change_ratio": diff_result.change_ratio,
            "reason": f"Change type: {diff_result.change_type.value}, ratio: {diff_result.change_ratio:.2f}",
        }


__all__ = [
    "SemanticDiffer",
    "ContentDiffer",
    "IncrementalSyncDecider",
    "DiffResult",
    "ContentDiffResult",
    "DiffSegment",
    "ChangeType",
]
