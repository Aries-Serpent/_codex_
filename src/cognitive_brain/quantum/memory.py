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
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import deque
import numpy as np

from cognitive_brain.quantum.config import QuantumConfig


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
    features: Dict[str, float]
    decision: str
    confidence: float
    timestamp: datetime
    access_count: int = 0
    success_rate: float = 1.0  # Assume success until proven otherwise
    last_accessed: Optional[datetime] = None
    in_ltm: bool = False
    
    def __post_init__(self):
        """Validate pattern data after initialization."""
        # Validate pattern_id
        if self.pattern_id is None or self.pattern_id == '':
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
    
    def __init__(self, config: QuantumConfig, stm_capacity: int = 1000, 
                 ltm_capacity: int = 10000, consolidation_threshold: float = 0.7):
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
        self.ltm: Dict[str, MemoryPattern] = {}
        
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
    
    def consolidate(self) -> int:
        """
        Consolidate patterns from STM to LTM (hippocampus → cortex).
        
        Promotion criteria:
        1. High access count (frequently referenced)
        2. High success rate (reliable pattern)
        3. Pattern distinctiveness (not too similar to existing LTM patterns)
        
        Returns:
            Number of patterns consolidated
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
        
        return consolidated_count
    
    def retrieve_similar(self, query: Dict[str, float], k: int = 5, 
                        search_ltm: bool = True) -> List[MemoryPattern]:
        """
        Retrieve k most similar patterns.
        
        Uses cosine similarity for feature matching with temporal decay factor.
        
        Args:
            query: Query features (normalized dict)
            k: Number of similar patterns to retrieve
            search_ltm: Whether to search long-term memory (default: True)
            
        Returns:
            List of k most similar patterns, sorted by similarity (highest first)
        """
        self.total_retrievals += 1
        
        # Combine STM and LTM for search
        search_space = list(self.stm)
        if search_ltm:
            search_space.extend(self.ltm.values())
        
        if not search_space:
            return []
        
        # Calculate similarity scores
        similarities = []
        current_time = datetime.now()
        
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
    
    def memory_guided_decision(self, query: Dict[str, float], 
                              confidence_threshold: float = 0.85) -> Optional[str]:
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
        self.total_retrievals += 1  # Track all guided decision attempts
        
        similar_patterns = self.retrieve_similar(query, k=5, search_ltm=True)
        
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
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with memory metrics
        """
        return {
            'stm_size': len(self.stm),
            'ltm_size': len(self.ltm),
            'stm_capacity': self.stm_capacity,
            'ltm_capacity': self.ltm_capacity,
            'total_stored': self.total_patterns_stored,
            'total_consolidated': self.total_patterns_consolidated,
            'total_retrievals': self.total_retrievals,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': self.get_cache_hit_rate(),
            'consolidation_rate': (
                self.total_patterns_consolidated / self.total_patterns_stored
                if self.total_patterns_stored > 0 else 0.0
            )
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
        score = (
            0.4 * access_score +
            0.4 * pattern.success_rate +
            0.2 * pattern.confidence
        )
        
        return score
    
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
            self.ltm.items(),
            key=lambda x: x[1].last_accessed or x[1].timestamp
        )
        
        # Remove oldest patterns
        for pattern_id, _ in sorted_patterns[:count]:
            del self.ltm[pattern_id]
    
    @staticmethod
    def _cosine_similarity(features1: Dict[str, float], features2: Dict[str, float]) -> float:
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
