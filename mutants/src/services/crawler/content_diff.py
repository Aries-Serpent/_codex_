"""Content Diffing for Knowledge Crawler.

PS-06 Enhancement: Implements partial article change detection:
- Detect partial article changes for micro-updates
- Enable micro-updates for minor changes
- Semantic diffing for knowledge base content

This module extends the Knowledge Crawler Service with
intelligent content diffing to minimize unnecessary re-syncs.
"""

from __future__ import annotations

import difflib
import hashlib
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Type of content change detected."""

    NO_CHANGE = "no_change"
    MINOR = "minor"  # Typos, formatting
    MODERATE = "moderate"  # Paragraph changes
    MAJOR = "major"  # Structural changes
    COMPLETE = "complete"  # Complete rewrite


@dataclass
class DiffSegment:
    """A segment of text that was changed."""

    change_type: str  # "insert", "delete", "replace"
    old_content: str
    new_content: str
    line_start: int
    line_end: int

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "change_type": self.change_type,
            "old_content_preview": (
                self.old_content[:100] + "..." if len(self.old_content) > 100 else self.old_content
            ),
            "new_content_preview": (
                self.new_content[:100] + "..." if len(self.new_content) > 100 else self.new_content
            ),
            "line_start": self.line_start,
            "line_end": self.line_end,
        }


@dataclass
class ContentDiffResult:
    """Result of content comparison."""

    change_type: ChangeType
    change_ratio: float  # 0.0 = identical, 1.0 = completely different
    similarity_ratio: float  # 1.0 = identical, 0.0 = completely different
    old_hash: str
    new_hash: str
    segments: list[DiffSegment] = field(default_factory=list)
    old_line_count: int = 0
    new_line_count: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    lines_modified: int = 0

    @property
    def has_changes(self) -> bool:
        """Check if there are any changes between old and new content.

        Returns:
            True if changes were detected, False otherwise
        """
        return self.change_type != ChangeType.NO_CHANGE

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "change_type": self.change_type.value,
            "change_ratio": round(self.change_ratio, 4),
            "similarity_ratio": round(self.similarity_ratio, 4),
            "old_hash": self.old_hash,
            "new_hash": self.new_hash,
            "old_line_count": self.old_line_count,
            "new_line_count": self.new_line_count,
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "lines_modified": self.lines_modified,
            "segment_count": len(self.segments),
            "segments": [s.to_dict() for s in self.segments[:10]],  # Limit to first 10
        }

    def should_sync(self, min_change_ratio: float = 0.01) -> bool:
        """Determine if content should be synced based on change ratio.

        Args:
            min_change_ratio: Minimum change ratio to trigger sync (default 1%)

        Returns:
            True if content should be synced
        """
        return self.change_ratio >= min_change_ratio


class ContentDiffer:
    """Intelligent content differ for knowledge base articles.

    Features:
    - Line-by-line diff comparison
    - Change classification (minor/moderate/major)
    - HTML-aware diffing
    - Semantic similarity calculation
    """

    # Thresholds for change classification
    MINOR_THRESHOLD = 0.05  # < 5% change
    MODERATE_THRESHOLD = 0.25  # < 25% change
    MAJOR_THRESHOLD = 0.75  # < 75% change

    def __init__(
        self,
        min_change_ratio: float = 0.01,
        strip_html: bool = True,
        ignore_whitespace: bool = True,
    ):
        """Initialize the content differ.

        Args:
            min_change_ratio: Minimum change to report (default 1%)
            strip_html: Strip HTML tags before comparison
            ignore_whitespace: Normalize whitespace before comparison
        """
        self.min_change_ratio = min_change_ratio
        self.strip_html = strip_html
        self.ignore_whitespace = ignore_whitespace

    @staticmethod
    def _hash_content(content: str) -> str:
        """Generate SHA-256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def _normalize_content(self, content: str) -> str:
        """Normalize content for comparison.

        Args:
            content: Raw content string

        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r"<[^>]+>", " ", content)
            # Decode HTML entities
            content = re.sub(r"&[a-z]+;", " ", content)

        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r"\s+", " ", content)
            content = "\n".join(line.strip() for line in content.split("\n"))

        return content.strip()

    def _classify_change(self, change_ratio: float) -> ChangeType:
        """Classify the change based on ratio.

        Args:
            change_ratio: Ratio of change (0.0 to 1.0)

        Returns:
            ChangeType classification
        """
        if change_ratio == 0:
            return ChangeType.NO_CHANGE
        if change_ratio < self.MINOR_THRESHOLD:
            return ChangeType.MINOR
        if change_ratio < self.MODERATE_THRESHOLD:
            return ChangeType.MODERATE
        if change_ratio < self.MAJOR_THRESHOLD:
            return ChangeType.MAJOR
        return ChangeType.COMPLETE

    def diff(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.

        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison

        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content

        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)

        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )

        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()

        # Use SequenceMatcher for similarity calculation (autojunk=False for accurate ratio)
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized, autojunk=False)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio

        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))

        lines_added = sum(1 for line in diff_lines if line.startswith("+ "))
        lines_removed = sum(1 for line in diff_lines if line.startswith("- "))
        lines_modified = sum(1 for line in diff_lines if line.startswith("? "))

        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)

        # Classify change type
        change_type = self._classify_change(change_ratio)

        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )

    def _extract_segments(
        self,
        old_lines: list[str],
        new_lines: list[str],
    ) -> list[DiffSegment]:
        """Extract changed segments from line diff.

        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content

        Returns:
            List of DiffSegment objects
        """
        segments = []

        # Use unified diff for segment extraction
        diff = list(
            difflib.unified_diff(
                old_lines,
                new_lines,
                lineterm="",
            )
        )

        current_segment = None
        line_num = 0

        for line in diff:
            if line.startswith("@@"):
                # Parse line numbers from diff header
                match = re.match(r"@@ -(\d+)", line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith("-") and not line.startswith("---"):
                if current_segment and current_segment.change_type == "delete":
                    current_segment.old_content += "\n" + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type="delete",
                        old_content=line[1:],
                        new_content="",
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith("+") and not line.startswith("+++"):
                if current_segment and current_segment.change_type == "insert":
                    current_segment.new_content += "\n" + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == "delete":
                    # Convert delete to replace
                    current_segment.change_type = "replace"
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type="insert",
                        old_content="",
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1

        if current_segment:
            segments.append(current_segment)

        return segments

    def should_resync(
        self,
        old_content: str,
        new_content: str,
    ) -> tuple[bool, ChangeType, float]:
        """Quick check if content should be resynced.

        Args:
            old_content: Previous content version
            new_content: New content version

        Returns:
            Tuple of (should_resync, change_type, change_ratio)
        """
        result = self.diff(old_content, new_content)
        return (
            result.should_sync(self.min_change_ratio),
            result.change_type,
            result.change_ratio,
        )


class IncrementalSyncDecider:
    """Decision logic for incremental sync based on content diffs.

    Uses content diffing to determine the optimal sync strategy:
    - Skip: No changes or changes below threshold
    - Micro-update: Minor changes, update only changed sections
    - Full update: Major changes, re-sync entire article
    """

    def __init__(
        self,
        differ: Optional[ContentDiffer] = None,
        micro_update_threshold: float = 0.10,  # <10% change
        full_update_threshold: float = 0.50,  # >50% change
    ):
        """Initialize the sync decider.

        Args:
            differ: ContentDiffer instance
            micro_update_threshold: Max change for micro-update
            full_update_threshold: Min change for full update
        """
        self.differ = differ or ContentDiffer()
        self.micro_update_threshold = micro_update_threshold
        self.full_update_threshold = full_update_threshold

    def decide(
        self,
        old_content: str,
        new_content: str,
    ) -> dict[str, Any]:
        """Decide sync strategy for content change.

        Args:
            old_content: Previous content version
            new_content: New content version

        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)

        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }

        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }

        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }

        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }


class SemanticDiffer:
    """Semantic content differ using embeddings.

    PS-06 P4 Enhancement: Upgrades content diffing from line-based to
    semantic-based using embeddings to reduce noise in knowledge drift alerts.

    Example:
        >>> differ = SemanticDiffer(similarity_threshold=0.98)
        >>> result = differ.compute_semantic_diff(old_text, new_text)
        >>> if result.is_semantically_similar:
        ...     print("No significant semantic change")
    """

    def __init__(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.

        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range

        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.metrics.pairwise import cosine_similarity

                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000, stop_words="english", ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(
                    f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})"
                )
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )

    def compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)

        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])

            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]

            return float(similarity)

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.error("Semantic similarity computation failed: <ERROR_TYPE>")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)

    def _basic_similarity(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()

        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except (ValueError, TypeError, RuntimeError):
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error("TF-IDF similarity computation failed: <ERROR_TYPE>")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()

    def compute_semantic_diff(self, old_content: str, new_content: str) -> dict[str, Any]:
        """Compute semantic diff between content versions.

        Args:
            old_content: Original content
            new_content: New content

        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)

        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(old_normalized, new_normalized)

        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold

        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite

        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }

    def _normalize_text(self, text: str) -> str:
        """Normalize text for semantic comparison.

        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove leading/trailing whitespace
        return text.strip()

    def should_resync(self, old_content: str, new_content: str) -> tuple[bool, dict[str, Any]]:
        """Determine if content should be resynced based on semantic diff.

        Args:
            old_content: Original content
            new_content: New content

        Returns:
            Tuple of (should_resync, diff_details)
        """
        diff_result = self.compute_semantic_diff(old_content, new_content)
        return diff_result["should_update"], diff_result


__all__ = [
    "ChangeType",
    "ContentDiffResult",
    "ContentDiffer",
    "DiffSegment",
    "IncrementalSyncDecider",
    "SemanticDiffer",
]
