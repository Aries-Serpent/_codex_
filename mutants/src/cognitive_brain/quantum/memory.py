"""
Quantum Memory Management System

Implements quantum-inspired memory management using hippocampus-cortex model
for pattern consolidation and retrieval. Enables memory-guided decision-making
through pattern reuse and similarity matching.

PDA Loop + AfterMath:
- PLAN: Define STM/LTM architecture, consolidation thresholds
- DO: Store patterns, consolidate to LTM, retrieve similar patterns
- ASSESS: Measure cache hit rate, consolidation success, retrieval accuracy
- AfterMath: Track memory efficiency, pattern reuse, k₁ improvement

Architecture inspired by biological memory systems:
- Short-term Memory (STM): Hippocampus-like rapid encoding (1000 capacity)
- Long-term Memory (LTM): Cortex-like compressed storage (10,000 capacity)
- Consolidation: Promotion based on access frequency and success rate
- Retrieval: Similarity-based search with temporal decay

Phase 8.1.1 Enhancements:
- Cache pruning by age, access frequency, and confidence
- Auto-pruning with configurable thresholds
- Cache health monitoring
"""

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, Optional

import numpy as np

from cognitive_brain.quantum.config import QuantumConfig

# Configure logging
logger = logging.getLogger(__name__)


class ConsolidationResult(int):
    """Result of a consolidation operation.

    Subclasses ``int`` for backward compatibility with callers that use the
    return value directly as a count.  New callers can use the ``.promoted``
    property for clarity.
    """

    @property
    def promoted(self) -> int:
        return self


@dataclass
class PruningResult:
    """Result of cache pruning operations."""

    aged_pruned: int = 0
    access_pruned: int = 0
    confidence_pruned: int = 0
    total_pruned: int = 0


@dataclass
class MemoryPattern:
    """
    Stored decision pattern with metadata for consolidation and retrieval.

    Attributes:
        pattern_id: Unique identifier for the pattern
        features: Normalized feature vector for similarity matching
        decision: The decision made for this pattern
        confidence: Confidence score of the decision (0.0-1.0)
        timestamp: When the pattern was created
        access_count: Number of times pattern has been retrieved
        success_rate: Success rate when this pattern was used (0.0-1.0)
        last_accessed: Last time the pattern was accessed
        in_ltm: Whether pattern is in long-term memory
    """

    pattern_id: str
    features: dict[str, float]
    decision: str
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    access_count: int = 0
    success_rate: float = 1.0  # Assume success until proven otherwise
    last_accessed: Optional[datetime] = None
    in_ltm: bool = False

    def __post_init__(self):
        """Validate pattern data after initialization."""
        # Validate pattern_id
        if self.pattern_id is None or self.pattern_id == "":
            raise ValueError("pattern_id must be non-empty string")

        # Validate confidence and success_rate ranges
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        if not 0.0 <= self.success_rate <= 1.0:
            raise ValueError(f"Success rate must be between 0 and 1, got {self.success_rate}")


class QuantumMemoryManager:
    """
    Quantum-inspired memory management system.

    Implements hippocampus-cortex model:
    - Hippocampus (STM): Rapid encoding, temporary storage
    - Cortex (LTM): Compressed, indexed long-term storage
    - Consolidation: Promotion of valuable patterns from STM to LTM
    - Retrieval: Similarity-based pattern matching

    Memory Architecture:
        STM: Recent patterns (last 24h or up to 1000 patterns)
        LTM: Consolidated patterns (up to 10,000 patterns)

    Consolidation Criteria:
        - Access count > threshold
        - Success rate > threshold
        - Pattern distinctiveness (not duplicate)
    """

    def __init__(
        self,
        config: QuantumConfig,
        stm_capacity: int = 1000,
        ltm_capacity: int = 10000,
        consolidation_threshold: float = 0.6,  # Lowered from 0.7 to allow high-quality patterns with moderate access  # noqa: E501
    ):
        """
        Initialize quantum memory manager.

        Args:
            config: Quantum configuration
            stm_capacity: Maximum short-term memory capacity
            ltm_capacity: Maximum long-term memory capacity
            consolidation_threshold: Threshold for STM → LTM promotion (0.0-1.0)
        """
        self.config = config
        self.stm_capacity = stm_capacity
        self.ltm_capacity = ltm_capacity
        self.consolidation_threshold = consolidation_threshold

        # Short-term memory (FIFO queue)
        self.stm: deque = deque(maxlen=stm_capacity)

        # Long-term memory (dict for fast lookup)
        self.ltm: dict[str, MemoryPattern] = {}

        # Statistics
        self.total_patterns_stored = 0
        self.total_patterns_consolidated = 0
        self.total_retrievals = 0
        self.cache_hits = 0

    def store_pattern(self, pattern: MemoryPattern) -> str:
        """
        Store new pattern in short-term memory.

        Args:
            pattern: Memory pattern to store (validated in __post_init__)

        Returns:
            Pattern ID
        """
        # Pattern validation handled in __post_init__
        # Add to STM
        self.stm.append(pattern)
        self.total_patterns_stored += 1

        return pattern.pattern_id

    def consolidate(self) -> "ConsolidationResult":
        """
        Consolidate patterns from STM to LTM (hippocampus → cortex).

        Promotion criteria:
        1. High access count (frequently referenced)
        2. High success rate (reliable pattern)
        3. Pattern distinctiveness (not too similar to existing LTM patterns)

        Returns:
            ConsolidationResult with `.promoted` count (also usable as int)
        """
        consolidated_count = 0
        patterns_to_promote = []

        # Check for LTM capacity
        if len(self.ltm) >= self.ltm_capacity:
            # Remove oldest LTM patterns to make space
            self._evict_old_ltm_patterns(count=100)

        # Evaluate STM patterns for promotion
        for pattern in self.stm:
            if pattern.in_ltm:
                continue  # Already in LTM

            # Calculate promotion score
            promotion_score = self._calculate_promotion_score(pattern)

            if promotion_score >= self.consolidation_threshold:
                # Check distinctiveness
                if self._is_distinctive(pattern):
                    patterns_to_promote.append(pattern)

        # Promote patterns to LTM
        for pattern in patterns_to_promote:
            pattern.in_ltm = True
            self.ltm[pattern.pattern_id] = pattern
            consolidated_count += 1
            self.total_patterns_consolidated += 1

        return ConsolidationResult(consolidated_count)

    def retrieve_similar(
        self,
        query: dict[str, float],
        k: int = 5,
        search_ltm: bool = True,
        count_retrieval: bool = True,
    ) -> list[MemoryPattern]:
        """
        Retrieve k most similar patterns.

        Uses cosine similarity for feature matching with temporal decay factor.

        Args:
            query: Query features (normalized dict)
            k: Number of similar patterns to retrieve
            search_ltm: Whether to search long-term memory (default: True)
            count_retrieval: Whether to count this as a retrieval (default: True)

        Returns:
            List of k most similar patterns, sorted by similarity (highest first)
        """
        if count_retrieval:
            self.total_retrievals += 1

        # Combine STM and LTM for search
        search_space = list(self.stm)
        if search_ltm:
            search_space.extend(self.ltm.values())

        if not search_space:
            return []

        # Calculate similarity scores
        similarities = []
        current_time = datetime.now(timezone.utc)

        for pattern in search_space:
            # Cosine similarity
            similarity = self._cosine_similarity(query, pattern.features)

            # Apply temporal decay (older patterns have lower weight)
            time_diff = (current_time - pattern.timestamp).total_seconds()
            decay_factor = np.exp(-time_diff / (86400 * 7))  # 1 week half-life

            # Combined score
            score = similarity * decay_factor
            similarities.append((pattern, score))

        # Sort by similarity (descending) and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_k = [pattern for pattern, _ in similarities[:k]]

        # Update access metadata
        for pattern in top_k:
            pattern.access_count += 1
            pattern.last_accessed = current_time

        return top_k

    def memory_guided_decision(
        self, query: dict[str, float], confidence_threshold: float = 0.85
    ) -> Optional[str]:
        """
        Make decision based on memory (cached pattern).

        Returns cached decision if:
        1. Similar patterns found (k=5)
        2. All similar patterns agree on decision
        3. Average confidence > threshold

        Note: This method tracks cache hits for memory-guided decisions specifically.
        For general retrieval statistics, use retrieve_similar().

        Args:
            query: Query features
            confidence_threshold: Minimum confidence for cache hit (default: 0.85)

        Returns:
            Cached decision if confident, None if novel case (run full assessment)
        """
        # Track retrieval attempt (don't double-count with retrieve_similar call)
        self.total_retrievals += 1

        similar_patterns = self.retrieve_similar(query, k=5, search_ltm=True, count_retrieval=False)

        if not similar_patterns:
            return None  # No patterns found - novel case

        # Check if all similar patterns agree
        decisions = [p.decision for p in similar_patterns]
        if len(set(decisions)) > 1:
            return None  # Disagreement - run full assessment

        # Check average confidence
        avg_confidence = sum(p.confidence for p in similar_patterns) / len(similar_patterns)
        if avg_confidence < confidence_threshold:
            return None  # Low confidence - run full assessment

        # Cache hit!
        self.cache_hits += 1
        return decisions[0]

    def get_cache_hit_rate(self) -> float:
        """
        Calculate cache hit rate.

        Returns:
            Cache hit rate (0.0-1.0) or 0.0 if no retrievals
        """
        if self.total_retrievals == 0:
            return 0.0
        return self.cache_hits / self.total_retrievals

    def get_statistics(self) -> dict[str, Any]:
        """
        Get memory statistics.

        Returns:
            Dictionary with memory metrics
        """
        return {
            "stm_size": len(self.stm),
            "ltm_size": len(self.ltm),
            "stm_capacity": self.stm_capacity,
            "ltm_capacity": self.ltm_capacity,
            "total_stored": self.total_patterns_stored,
            "total_consolidated": self.total_patterns_consolidated,
            "total_retrievals": self.total_retrievals,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.get_cache_hit_rate(),
            "consolidation_rate": (
                self.total_patterns_consolidated / self.total_patterns_stored
                if self.total_patterns_stored > 0
                else 0.0
            ),
        }

    def _calculate_promotion_score(self, pattern: MemoryPattern) -> float:
        """
        Calculate promotion score for STM → LTM consolidation.

        Score based on:
        - Access frequency (normalized by max observed)
        - Success rate (0.0-1.0)
        - Confidence (0.0-1.0)

        Returns:
            Promotion score (0.0-1.0)
        """
        # Normalize access count (assume max 100 accesses is very high)
        access_score = min(pattern.access_count / 100.0, 1.0)

        # Weighted combination
        return 0.4 * access_score + 0.4 * pattern.success_rate + 0.2 * pattern.confidence

    def _is_distinctive(self, pattern: MemoryPattern, threshold: float = 0.95) -> bool:
        """
        Check if pattern is distinctive enough for LTM.

        Args:
            pattern: Pattern to check
            threshold: Similarity threshold (patterns above this are too similar)

        Returns:
            True if pattern is distinctive (not too similar to existing LTM)
        """
        if not self.ltm:
            return True  # No LTM patterns yet

        # Check similarity to existing LTM patterns
        for ltm_pattern in self.ltm.values():
            similarity = self._cosine_similarity(pattern.features, ltm_pattern.features)
            if similarity > threshold:
                return False  # Too similar to existing pattern

        return True

    def _evict_old_ltm_patterns(self, count: int = 100) -> None:
        """
        Evict oldest LTM patterns to free space.

        Args:
            count: Number of patterns to evict
        """
        if not self.ltm:
            return

        # Sort by last access time (oldest first)
        sorted_patterns = sorted(
            self.ltm.items(), key=lambda x: x[1].last_accessed or x[1].timestamp
        )

        # Remove oldest patterns
        for pattern_id, _ in sorted_patterns[:count]:
            del self.ltm[pattern_id]

    @staticmethod
    def _cosine_similarity(features1: dict[str, float], features2: dict[str, float]) -> float:
        """
        Calculate cosine similarity between two feature vectors.

        Args:
            features1: First feature dict
            features2: Second feature dict

        Returns:
            Cosine similarity (0.0-1.0)
        """
        # Get common keys
        common_keys = set(features1.keys()) & set(features2.keys())
        if not common_keys:
            return 0.0

        # Calculate dot product and magnitudes
        dot_product = sum(features1[k] * features2[k] for k in common_keys)
        magnitude1 = np.sqrt(sum(features1[k] ** 2 for k in common_keys))
        magnitude2 = np.sqrt(sum(features2[k] ** 2 for k in common_keys))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    #####################################################
    # PHASE 8.1.1 ENHANCEMENTS: CACHE PRUNING & MANAGEMENT
    #####################################################

    def prune_by_age(self, max_age_hours: float = 720) -> int:
        """
        Remove patterns older than specified age from LTM.

        Implements time-based cache cleanup to prevent stale patterns
        from consuming memory indefinitely.

        Args:
            max_age_hours: Maximum age in hours (default: 30 days = 720 hours)

        Returns:
            Number of patterns pruned
        """
        now = datetime.now(timezone.utc)
        max_age_delta = timedelta(hours=max_age_hours)

        pruned_count = 0
        patterns_to_remove = []

        for pattern_id, pattern in self.ltm.items():
            age = now - pattern.timestamp
            if age > max_age_delta:
                patterns_to_remove.append(pattern_id)

        for pattern_id in patterns_to_remove:
            del self.ltm[pattern_id]
            pruned_count += 1

        if pruned_count > 0:
            logger.info(f"Pruned {pruned_count} patterns older than {max_age_hours}h from LTM")

        return pruned_count

    def prune_by_access(self, keep_top_n: int = 5000) -> int:
        """
        Keep only the most frequently accessed patterns (LRU policy).

        Implements access-based cache cleanup to prioritize frequently
        used patterns and remove rarely accessed ones.

        Args:
            keep_top_n: Number of top patterns to keep (default: 5000 = 50% of LTM capacity)

        Returns:
            Number of patterns pruned
        """
        if len(self.ltm) <= keep_top_n:
            return 0

        # Sort by access count (descending), then by last_accessed (recent first)
        sorted_patterns = sorted(
            self.ltm.items(),
            key=lambda x: (x[1].access_count, x[1].last_accessed or x[1].timestamp),
            reverse=True,
        )

        # Keep top N, remove rest
        patterns_to_remove = [pid for pid, _ in sorted_patterns[keep_top_n:]]

        for pattern_id in patterns_to_remove:
            del self.ltm[pattern_id]

        pruned_count = len(patterns_to_remove)
        if pruned_count > 0:
            logger.info(
                f"Pruned {pruned_count} least accessed patterns from LTM (kept top {keep_top_n})"
            )

        return pruned_count

    def prune_low_confidence(self, min_confidence: float = 0.5) -> int:
        """
        Remove patterns with low confidence scores from LTM.

        Implements quality-based cache cleanup to remove unreliable patterns.

        Args:
            min_confidence: Minimum confidence threshold (default: 0.5)

        Returns:
            Number of patterns pruned
        """
        patterns_to_remove = [
            pattern_id
            for pattern_id, pattern in self.ltm.items()
            if pattern.confidence < min_confidence
        ]

        for pattern_id in patterns_to_remove:
            del self.ltm[pattern_id]

        pruned_count = len(patterns_to_remove)
        if pruned_count > 0:
            logger.info(
                f"Pruned {pruned_count} low-confidence patterns (<{min_confidence}) from LTM"
            )

        return pruned_count

    def get_cache_health(self) -> dict[str, Any]:
        """
        Get comprehensive cache health metrics for monitoring.

        Returns:
            Dictionary with health metrics:
            - stm_size: Current STM size
            - ltm_size: Current LTM size
            - stm_utilization: STM utilization percentage
            - ltm_utilization: LTM utilization percentage
            - cache_hit_rate: Overall cache hit rate
            - avg_age_hours: Average pattern age in hours
            - avg_access_count: Average pattern access count
            - staleness_score: Percentage of patterns >30 days old (configurable threshold)
        """
        STALENESS_THRESHOLD_HOURS = 720  # 30 days, matches default in prune_by_age()

        stm_size = len(self.stm)
        ltm_size = len(self.ltm)

        # Calculate average age
        now = datetime.now(timezone.utc)
        if ltm_size > 0:
            ages = [(now - p.timestamp).total_seconds() / 3600 for p in self.ltm.values()]
            avg_age_hours = sum(ages) / len(ages)
            staleness_score = (
                sum(1 for age in ages if age > STALENESS_THRESHOLD_HOURS) / len(ages) * 100
            )
        else:
            avg_age_hours = 0.0
            staleness_score = 0.0

        # Calculate average access count
        if ltm_size > 0:
            avg_access_count = sum(p.access_count for p in self.ltm.values()) / ltm_size
        else:
            avg_access_count = 0.0

        return {
            "stm_size": stm_size,
            "ltm_size": ltm_size,
            "stm_utilization": (
                (stm_size / self.stm_capacity * 100) if self.stm_capacity > 0 else 0.0
            ),
            "ltm_utilization": (
                (ltm_size / self.ltm_capacity * 100) if self.ltm_capacity > 0 else 0.0
            ),
            "cache_hit_rate": self.get_cache_hit_rate(),
            "avg_age_hours": avg_age_hours,
            "avg_access_count": avg_access_count,
            "staleness_score": staleness_score,
        }

    def auto_prune(self, ltm_threshold_pct: float = 0.8) -> PruningResult:
        """
        Automatically prune cache based on configurable thresholds.

        Triggered when LTM utilization exceeds threshold. Applies multiple
        pruning strategies to maintain optimal cache health.

        Args:
            ltm_threshold_pct: LTM utilization threshold to trigger pruning (default: 0.8 = 80%)

        Returns:
            PruningResult with counts for each pruning strategy
        """
        health = self.get_cache_health()

        if health["ltm_utilization"] < ltm_threshold_pct * 100:
            return PruningResult()

        logger.info(f"Auto-pruning triggered: LTM at {health['ltm_utilization']:.1f}% capacity")

        # Strategy 1: Remove patterns older than 30 days
        aged_pruned = self.prune_by_age(max_age_hours=720)

        # Strategy 2: If still above threshold, keep only top 50% by access
        health = self.get_cache_health()
        if health["ltm_utilization"] > ltm_threshold_pct * 100:
            access_pruned = self.prune_by_access(keep_top_n=self.ltm_capacity // 2)
        else:
            access_pruned = 0

        # Strategy 3: Remove low confidence patterns (< 0.5)
        confidence_pruned = self.prune_low_confidence(min_confidence=0.5)

        total_pruned = aged_pruned + access_pruned + confidence_pruned
        logger.info(f"Auto-pruning complete: {total_pruned} patterns removed")

        return PruningResult(
            aged_pruned=aged_pruned,
            access_pruned=access_pruned,
            confidence_pruned=confidence_pruned,
            total_pruned=total_pruned,
        )
