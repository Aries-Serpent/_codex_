#!/usr/bin/env python3
"""
Context Injection System - Phase 10.3 Days 4-5

Implements context injection for OODA loop with:
- Historical pattern matching (cosine similarity)
- Decision context assembly from multiple sources
- Confidence scoring & uncertainty quantification
- Multi-source context fusion
- Context relevance filtering (top-K selection)
- Graceful degradation

Target Performance:
- Pattern search: < 30ms for top-5 patterns
- Context assembly: < 20ms
- Total overhead: < 5% of 200ms cycle time
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfidenceSource(Enum):
    """Sources of confidence in context quality."""
    PATTERN_SIMILARITY = "pattern_similarity"
    PATTERN_SAMPLE_SIZE = "pattern_sample_size"
    SESSION_RECENCY = "session_recency"
    CONTEXT_COMPLETENESS = "context_completeness"


@dataclass
class ConfidenceMetrics:
    """Confidence scoring details."""
    pattern_similarity_score: float = 0.0  # 0-1
    session_recency_score: float = 0.0  # 0-1
    external_reliability: float = 0.0  # 0-1
    pattern_sample_size_score: float = 0.0  # 0-1
    overall_confidence: float = 0.0  # 0-1 (weighted average)
    breakdown: Dict[str, float] = field(default_factory=dict)


@dataclass
class ContextMetadata:
    """Metadata about context quality."""
    source: str  # "patterns", "sessions", "external"
    freshness_ms: int  # How old is the data
    reliability: float  # 0-1 estimate of data quality
    completeness: float  # 0-1 estimate of coverage


class PatternStore(ABC):
    """Abstract interface for pattern storage (Track 10.2 integration)."""
    
    @abstractmethod
    async def search_similar(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        min_similarity: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Find similar patterns by vector similarity.
        
        Returns list of patterns with similarity scores.
        """
        pass
    
    @abstractmethod
    async def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific pattern by ID."""
        pass
    
    @abstractmethod
    async def get_patterns_by_tag(self, tag: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get patterns by tag (e.g., 'ci_self_healing', 'ml_pattern_feeding')."""
        pass


class SessionStore(ABC):
    """Abstract interface for session storage (Track 10.1 integration)."""
    
    @abstractmethod
    async def get_sessions(
        self,
        task_type: str,
        limit: int = 3,
        success_only: bool = True,
        max_age_days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get recent sessions of a specific task type."""
        pass
    
    @abstractmethod
    async def get_decision_history(
        self,
        task_type: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get historical decisions for a task type."""
        pass


class VectorEncoder:
    """Encode observations into vectors for similarity matching."""
    
    def __init__(self, vector_size: int = 128):
        self.vector_size = vector_size
    
    def encode_observation(self, observation: Dict[str, Any]) -> np.ndarray:
        """
        Encode observation data into fixed-size vector.
        
        Combines:
        - Task type (one-hot encoding)
        - Priority level (ordinal)
        - Queue depth (normalized)
        - CI health (normalized)
        - Repository state (hash-based)
        """
        vector = np.zeros(self.vector_size)
        
        # Task type encoding (first 16 dims)
        task_type = observation.get("task", {}).get("type", "unknown")
        task_type_hash = hash(task_type) % 16
        vector[task_type_hash] = 1.0
        
        # Priority encoding (dims 16-20)
        priority_map = {"P0": 1.0, "P1": 0.75, "P2": 0.5, "P3": 0.25}
        priority = observation.get("task", {}).get("priority", "P2")
        vector[16] = priority_map.get(priority, 0.5)
        
        # Queue depth normalization (dim 17)
        queue_depth = observation.get("agent_state", {}).get("queue_depth", 0)
        vector[17] = min(queue_depth / 100.0, 1.0)
        
        # CI health (dim 18)
        ci_health = observation.get("environment", {}).get("ci_health", 0.5)
        vector[18] = float(ci_health)
        
        # Success rate (dim 19)
        success_rate = observation.get("agent_state", {}).get("performance", {}).get("success_rate", 0.5)
        vector[19] = float(success_rate)
        
        # Random padding (remaining dims) - in production, use learned embeddings
        np.random.seed(hash(str(observation)) % 2**32)
        vector[20:] = np.random.normal(0.5, 0.1, self.vector_size - 20)
        
        # Normalize to unit vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector


class ContextInjector:
    """Main context injection engine for OODA loop."""
    
    def __init__(
        self,
        pattern_store: PatternStore,
        session_store: SessionStore,
        vector_encoder: Optional[VectorEncoder] = None,
        max_pattern_age_days: int = 90,
        max_session_age_days: int = 30,
    ):
        """
        Initialize context injector.
        
        Args:
            pattern_store: LTM pattern storage (Track 10.2)
            session_store: Session checkpoint storage (Track 10.1)
            vector_encoder: Optional custom vector encoder
            max_pattern_age_days: Max age for patterns to be relevant
            max_session_age_days: Max age for sessions to be relevant
        """
        self.pattern_store = pattern_store
        self.session_store = session_store
        self.vector_encoder = vector_encoder or VectorEncoder()
        self.max_pattern_age_days = max_pattern_age_days
        self.max_session_age_days = max_session_age_days
        
        # Metrics
        self.metrics = {
            "total_context_requests": 0,
            "patterns_retrieved": 0,
            "sessions_retrieved": 0,
            "avg_pattern_similarity": 0.0,
            "confidence_scores": [],
        }
    
    async def inject_context(
        self,
        observation: Dict[str, Any],
        top_k_patterns: int = 5,
        top_k_sessions: int = 3,
        timeout_ms: int = 50,
    ) -> Tuple[Dict[str, Any], ConfidenceMetrics, ContextMetadata]:
        """
        Inject context from all sources.
        
        Args:
            observation: Observation from OODA phase 1
            top_k_patterns: Number of top patterns to retrieve
            top_k_sessions: Number of top sessions to retrieve
            timeout_ms: Max time to spend on context injection
        
        Returns:
            (context_dict, confidence_metrics, metadata)
        """
        start_time = time.time()
        
        context = {
            "patterns": [],
            "sessions": [],
            "external": {},
        }
        
        self.metrics["total_context_requests"] += 1
        
        try:
            # Parallel context retrieval
            pattern_task = asyncio.create_task(
                self._get_patterns(observation, top_k_patterns)
            )
            session_task = asyncio.create_task(
                self._get_sessions(observation, top_k_sessions)
            )
            external_task = asyncio.create_task(
                self._get_external_context()
            )
            
            # Wait with timeout
            timeout_sec = timeout_ms / 1000.0
            done, pending = await asyncio.wait(
                [pattern_task, session_task, external_task],
                timeout=timeout_sec,
            )
            
            # Collect results
            if pattern_task in done:
                context["patterns"] = await pattern_task
                self.metrics["patterns_retrieved"] += len(context["patterns"])
            
            if session_task in done:
                context["sessions"] = await session_task
                self.metrics["sessions_retrieved"] += len(context["sessions"])
            
            if external_task in done:
                context["external"] = await external_task
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
        
        except asyncio.TimeoutError:
            logger.warning(f"Context injection timeout after {timeout_ms}ms")
        except Exception as e:
            logger.error(f"Context injection error: {e}")
        
        # Calculate confidence metrics
        confidence = self._calculate_confidence(context, observation)
        
        # Create metadata
        elapsed_ms = int((time.time() - start_time) * 1000)
        metadata = ContextMetadata(
            source="multi_source",
            freshness_ms=elapsed_ms,
            reliability=confidence.overall_confidence,
            completeness=self._calculate_completeness(context),
        )
        
        return context, confidence, metadata
    
    async def _get_patterns(
        self,
        observation: Dict[str, Any],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Retrieve similar patterns from LTM."""
        try:
            # Encode observation as vector
            obs_vector = self.vector_encoder.encode_observation(observation)

            # Search pattern store
            patterns = await asyncio.wait_for(
                self.pattern_store.search_similar(obs_vector, top_k=top_k),
                timeout=0.04,  # 40ms max for pattern search
            )

            if not isinstance(patterns, list):
                return []
            return patterns[: max(0, int(top_k))]
        except Exception as e:
            logger.warning(f"Pattern retrieval failed: {e}")
            return []

    async def _get_sessions(
        self,
        observation: Dict[str, Any],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant sessions from checkpoint storage."""
        try:
            task_type = observation.get("task", {}).get("type", "unknown")

            sessions = await asyncio.wait_for(
                self.session_store.get_sessions(
                    task_type=task_type,
                    limit=top_k,
                    success_only=True,
                    max_age_days=self.max_session_age_days,
                ),
                timeout=0.03,  # 30ms max for session retrieval
            )

            if not isinstance(sessions, list):
                return []
            return sessions[: max(0, int(top_k))]
        except Exception as e:
            logger.warning(f"Session retrieval failed: {e}")
            return []
    
    async def _get_external_context(self) -> Dict[str, Any]:
        """Retrieve external context (GitHub advisory, repo vars, CI health)."""
        try:
            # In production, this would fetch from:
            # - GitHub advisory database
            # - Repository variables (CODEX_* env vars)
            # - CI health metrics
            external = {
                "advisory_issues": [],
                "repo_variables": {},
                "ci_health": 0.85,
            }
            return external
        except Exception as e:
            logger.warning(f"External context retrieval failed: {e}")
            return {}
    
    def _calculate_confidence(
        self,
        context: Dict[str, Any],
        observation: Dict[str, Any],
    ) -> ConfidenceMetrics:
        """Calculate confidence scores based on context quality."""
        metrics = ConfidenceMetrics()
        
        # Pattern similarity score (max similarity of top patterns)
        if context["patterns"]:
            max_similarity = max(
                p.get("similarity", 0) for p in context["patterns"]
            )
            metrics.pattern_similarity_score = float(max_similarity)
        
        # Pattern sample size score (prefer patterns with many samples)
        if context["patterns"]:
            sample_size = context["patterns"][0].get("sample_size", 1)
            metrics.pattern_sample_size_score = min(sample_size / 100.0, 1.0)
        
        # Session recency score (prefer recent sessions)
        if context["sessions"]:
            session = context["sessions"][0]
            created_at = session.get("created_at")
            if created_at:
                try:
                    session_dt = datetime.fromisoformat(created_at)
                    age_hours = (datetime.now() - session_dt).total_seconds() / 3600
                    # Score: 1.0 if < 1 hour old, 0.5 if < 24 hours, 0.2 if > 7 days
                    if age_hours < 1:
                        metrics.session_recency_score = 1.0
                    elif age_hours < 24:
                        metrics.session_recency_score = 0.8
                    elif age_hours < 168:  # 7 days
                        metrics.session_recency_score = 0.5
                    else:
                        metrics.session_recency_score = 0.2
                except:
                    metrics.session_recency_score = 0.5
        
        # External reliability score
        external = context.get("external", {})
        if external:
            metrics.external_reliability = 0.8  # External data generally reliable
        
        # Overall confidence (weighted average)
        weights = {
            "pattern_similarity": 0.4,
            "session_recency": 0.3,
            "external_reliability": 0.2,
            "sample_size": 0.1,
        }
        
        metrics.overall_confidence = (
            metrics.pattern_similarity_score * weights["pattern_similarity"] +
            metrics.session_recency_score * weights["session_recency"] +
            metrics.external_reliability * weights["external_reliability"] +
            metrics.pattern_sample_size_score * weights["sample_size"]
        )
        
        metrics.breakdown = {
            "pattern_similarity": metrics.pattern_similarity_score,
            "session_recency": metrics.session_recency_score,
            "external_reliability": metrics.external_reliability,
            "sample_size": metrics.pattern_sample_size_score,
        }
        
        self.metrics["confidence_scores"].append(metrics.overall_confidence)
        
        return metrics
    
    def _calculate_completeness(self, context: Dict[str, Any]) -> float:
        """Calculate context completeness (0-1)."""
        score = 0.0
        
        if context.get("patterns"):
            score += 0.4
        
        if context.get("sessions"):
            score += 0.4
        
        if context.get("external"):
            score += 0.2
        
        return score
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get context injection metrics."""
        metrics = dict(self.metrics)
        
        if metrics["confidence_scores"]:
            metrics["avg_confidence"] = np.mean(metrics["confidence_scores"])
            metrics["median_confidence"] = np.median(metrics["confidence_scores"])
            metrics["p99_confidence"] = np.percentile(metrics["confidence_scores"], 99)
        
        return metrics


class ContextFusionEngine:
    """Fuse context from multiple sources with priority weighting."""
    
    @staticmethod
    def fuse_patterns(patterns: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Fuse multiple pattern results.
        
        Ranking by:
        1. Similarity score (primary)
        2. Success rate (secondary)
        3. Sample size (tertiary)
        """
        if not patterns:
            return []
        
        # Sort by weighted score
        def score_pattern(p):
            similarity = p.get("similarity", 0)
            success_rate = p.get("success_rate", 0.5)
            sample_size = min(p.get("sample_size", 1) / 100.0, 1.0)
            
            # Weighted score
            return similarity * 0.5 + success_rate * 0.3 + sample_size * 0.2
        
        sorted_patterns = sorted(patterns, key=score_pattern, reverse=True)
        return sorted_patterns[:top_k]
    
    @staticmethod
    def fuse_sessions(sessions: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Fuse multiple session results.
        
        Ranking by:
        1. Success (only successful sessions)
        2. Recency
        3. Duration efficiency
        """
        if not sessions:
            return []
        
        # Filter successful sessions
        successful = [s for s in sessions if s.get("success", False)]
        
        # Sort by recency
        def session_score(s):
            created_at = s.get("created_at")
            if created_at:
                try:
                    session_dt = datetime.fromisoformat(created_at)
                    age_hours = (datetime.now() - session_dt).total_seconds() / 3600
                    # Prefer recent sessions, penalize old ones
                    return 1.0 / (1.0 + age_hours / 24.0)
                except:
                    return 0.5
            return 0.5
        
        sorted_sessions = sorted(successful, key=session_score, reverse=True)
        return sorted_sessions[:top_k]


# Mock implementations for testing
class MockPatternStore(PatternStore):
    """Mock pattern store for testing."""
    
    def __init__(self):
        self.patterns = [
            {
                "pattern_id": "pat_001",
                "name": "CI Self-Healing Pattern",
                "similarity": 0.92,
                "success_rate": 0.88,
                "sample_size": 150,
                "tags": ["ci_self_healing", "automated"],
            },
            {
                "pattern_id": "pat_002",
                "name": "ML Pattern Feeding",
                "similarity": 0.75,
                "success_rate": 0.82,
                "sample_size": 45,
                "tags": ["ml_pattern_feeding"],
            },
        ]
    
    async def search_similar(self, query_vector, top_k=5, min_similarity=0.5):
        # Return top patterns (mocked)
        return [p for p in self.patterns if p.get("similarity", 0) >= min_similarity][:top_k]
    
    async def get_pattern(self, pattern_id):
        for p in self.patterns:
            if p["pattern_id"] == pattern_id:
                return p
        return None
    
    async def get_patterns_by_tag(self, tag, limit=10):
        return [p for p in self.patterns if tag in p.get("tags", [])][:limit]


class MockSessionStore(SessionStore):
    """Mock session store for testing."""
    
    async def get_sessions(self, task_type, limit=3, success_only=True, max_age_days=30):
        return [
            {
                "session_id": "sess_001",
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "task_type": task_type,
                "success": True,
                "duration_ms": 250,
            }
        ]
    
    async def get_decision_history(self, task_type, limit=10):
        return []


async def demo():
    """Demo context injection."""
    print("=" * 60)
    print("Context Injection System Demo")
    print("=" * 60)
    
    # Initialize
    pattern_store = MockPatternStore()
    session_store = MockSessionStore()
    injector = ContextInjector(pattern_store, session_store)
    
    # Sample observation
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
        "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
        "environment": {"ci_health": 0.85},
    }
    
    # Inject context
    context, confidence, metadata = await injector.inject_context(observation)
    
    print("\nContext retrieved:")
    print(f"- Patterns: {len(context['patterns'])}")
    print(f"- Sessions: {len(context['sessions'])}")
    print(f"- External context: {len(context['external'])} fields")
    print("\nConfidence Metrics:")
    print(f"- Overall: {confidence.overall_confidence:.2f}")
    print(f"- Pattern similarity: {confidence.pattern_similarity_score:.2f}")
    print(f"- Session recency: {confidence.session_recency_score:.2f}")
    print(f"- Metadata freshness: {metadata.freshness_ms}ms")


if __name__ == "__main__":
    asyncio.run(demo())
