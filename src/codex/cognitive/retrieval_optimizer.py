"""
Retrieval Optimizer - Phase 4.3 of Long-term Plan 4.

This module provides retrieval optimization capabilities for efficient
context loading, pre-fetching likely-needed patterns, and adaptive
retrieval based on task type.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RetrievalStrategy(Enum):
    """Strategies for retrieving context."""

    PROACTIVE = "proactive"  # Load relevant context at session start
    REACTIVE = "reactive"  # On-demand pattern lookup
    HYBRID = "hybrid"  # Proactive core + reactive expansion


class TaskType(Enum):
    """Types of tasks for adaptive retrieval."""

    BUG_FIX = "bug_fix"
    FEATURE = "feature"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    CI_CD = "ci_cd"
    SECURITY = "security"
    UNKNOWN = "unknown"


@dataclass
class RetrievalResult:
    """Result of a retrieval operation."""

    query: str
    items: list[dict[str, Any]]
    retrieval_time_ms: float
    strategy_used: RetrievalStrategy
    cache_hit: bool
    relevance_scores: list[float]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "item_count": len(self.items),
            "retrieval_time_ms": self.retrieval_time_ms,
            "strategy_used": self.strategy_used.value,
            "cache_hit": self.cache_hit,
            "average_relevance": (
                sum(self.relevance_scores) / len(self.relevance_scores)
                if self.relevance_scores
                else 0
            ),
        }


@dataclass
class RetrievalMetrics:
    """Metrics for retrieval performance."""

    total_queries: int = 0
    cache_hits: int = 0
    total_retrieval_time_ms: float = 0
    average_result_count: float = 0
    average_relevance: float = 0

    def record(self, result: RetrievalResult) -> None:
        """Record a retrieval result."""
        self.total_queries += 1
        if result.cache_hit:
            self.cache_hits += 1
        self.total_retrieval_time_ms += result.retrieval_time_ms

        # Rolling averages
        self.average_result_count = (
            self.average_result_count * (self.total_queries - 1) + len(result.items)
        ) / self.total_queries
        if result.relevance_scores:
            avg_rel = sum(result.relevance_scores) / len(result.relevance_scores)
            self.average_relevance = (
                self.average_relevance * (self.total_queries - 1) + avg_rel
            ) / self.total_queries

    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate."""
        return self.cache_hits / self.total_queries if self.total_queries > 0 else 0

    @property
    def average_retrieval_time_ms(self) -> float:
        """Get average retrieval time."""
        return self.total_retrieval_time_ms / self.total_queries if self.total_queries > 0 else 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_queries": self.total_queries,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.cache_hit_rate,
            "average_retrieval_time_ms": self.average_retrieval_time_ms,
            "average_result_count": self.average_result_count,
            "average_relevance": self.average_relevance,
        }


class RetrievalCache:
    """Cache for frequently retrieved items."""

    def __init__(self, max_size: int = 100):
        """Initialize cache."""
        self.max_size = max_size
        self._cache: dict[str, tuple[list[dict[str, Any]], datetime]] = {}

    def get(self, key: str, max_age_seconds: int = 300) -> list[dict[str, Any]] | None:
        """Get cached result if fresh."""
        if key not in self._cache:
            return None

        items, cached_at = self._cache[key]
        age = (datetime.now(timezone.utc) - cached_at).total_seconds()

        if age > max_age_seconds:
            del self._cache[key]
            return None

        return items

    def set(self, key: str, items: list[dict[str, Any]]) -> None:
        """Cache a result."""
        if len(self._cache) >= self.max_size:
            # Remove oldest
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        self._cache[key] = (items, datetime.now(timezone.utc))

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()

    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)


class TaskTypeDetector:
    """Detect task type from context."""

    TASK_KEYWORDS = {
        TaskType.BUG_FIX: ["fix", "bug", "error", "issue", "broken", "crash", "fail"],
        TaskType.FEATURE: ["add", "implement", "create", "feature", "new", "enhance"],
        TaskType.REFACTOR: ["refactor", "clean", "reorganize", "optimize", "simplify"],
        TaskType.DOCUMENTATION: ["doc", "readme", "comment", "explain", "document"],
        TaskType.TESTING: ["test", "coverage", "pytest", "unittest", "spec", "assert"],
        TaskType.CI_CD: ["ci", "cd", "workflow", "pipeline", "action", "deploy"],
        TaskType.SECURITY: ["security", "vulnerability", "cve", "secret", "credential"],
    }

    def detect(self, text: str) -> TaskType:
        """Detect task type from text."""
        text_lower = text.lower()

        scores: dict[TaskType, int] = {}
        for task_type, keywords in self.TASK_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[task_type] = score

        if not scores:
            return TaskType.UNKNOWN

        return max(scores.keys(), key=lambda t: scores[t])

    def detect_multiple(self, text: str) -> list[tuple[TaskType, int]]:
        """Detect multiple task types with scores."""
        text_lower = text.lower()

        scores: list[tuple[TaskType, int]] = []
        for task_type, keywords in self.TASK_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores.append((task_type, score))

        return sorted(scores, key=lambda x: x[1], reverse=True)


class RelevanceScorer:
    """Score relevance of retrieved items."""

    def __init__(self) -> None:
        """Initialize scorer."""
        self.task_detector = TaskTypeDetector()

    def score(
        self,
        item: dict[str, Any],
        query: str,
        task_type: TaskType | None = None,
    ) -> float:
        """Score relevance of an item to a query."""
        score = 0.0
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Content match
        content = str(item.get("content", "")).lower()
        content_words = set(content.split())
        word_overlap = len(query_words.intersection(content_words))
        score += min(word_overlap * 0.1, 0.5)

        # Direct substring match
        if query_lower in content:
            score += 0.3

        # Task type match
        if task_type:
            item_type = item.get("task_type")
            if item_type == task_type.value:
                score += 0.2

        # Recency boost
        created_at = item.get("created_at")
        if created_at:
            try:
                created = datetime.fromisoformat(created_at)
                days_old = (datetime.now(timezone.utc) - created).days
                recency_factor = max(0, 1 - days_old / 30)  # Decay over 30 days
                score += recency_factor * 0.2
            except (TypeError, ValueError):
                logger.debug("Suppressed exception in handler", exc_info=True)
        return min(score, 1.0)

    def score_batch(
        self,
        items: list[dict[str, Any]],
        query: str,
        task_type: TaskType | None = None,
    ) -> list[float]:
        """Score a batch of items."""
        return [self.score(item, query, task_type) for item in items]


class ProactiveLoader:
    """Load context proactively at session start."""

    def __init__(self, knowledge_store_path: Path | None = None):
        """Initialize loader."""
        self.store_path = knowledge_store_path or Path(".codex/knowledge/knowledge_store.json")
        self._knowledge_cache: list[dict[str, Any]] = []

    def load_knowledge_store(self) -> list[dict[str, Any]]:
        """Load knowledge store into cache."""
        if self.store_path.exists():
            try:
                with open(self.store_path) as f:
                    data = json.load(f)
                    self._knowledge_cache = data.get("items", [])
            except (json.JSONDecodeError, KeyError):
                self._knowledge_cache = []
        return self._knowledge_cache

    def get_critical_knowledge(self) -> list[dict[str, Any]]:
        """Get all critical knowledge items."""
        return [item for item in self._knowledge_cache if item.get("priority") == "critical"]

    def get_recent_knowledge(self, days: int = 7) -> list[dict[str, Any]]:
        """Get recent knowledge items."""
        cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
        results = []

        for item in self._knowledge_cache:
            try:
                created = datetime.fromisoformat(item.get("created_at", ""))
                if created.timestamp() > cutoff:
                    results.append(item)
            except (TypeError, ValueError):
                logger.debug("Suppressed exception in handler", exc_info=True)
        return results

    def get_task_relevant_knowledge(self, task_type: TaskType) -> list[dict[str, Any]]:
        """Get knowledge relevant to a task type."""
        task_keywords = TaskTypeDetector.TASK_KEYWORDS.get(task_type, [])
        results = []

        for item in self._knowledge_cache:
            content = str(item.get("content", "")).lower()
            if any(kw in content for kw in task_keywords):
                results.append(item)

        return results


class ReactiveRetriever:
    """Retrieve context on-demand."""

    def __init__(self, cache: RetrievalCache | None = None):
        """Initialize retriever."""
        self.cache = cache or RetrievalCache()
        self.scorer = RelevanceScorer()

    def retrieve(
        self,
        query: str,
        knowledge_items: list[dict[str, Any]],
        max_results: int = 10,
        min_relevance: float = 0.1,
    ) -> tuple[list[dict[str, Any]], list[float], bool]:
        """Retrieve relevant items for a query."""
        # Check cache
        cached = self.cache.get(query)
        if cached is not None:
            scores = self.scorer.score_batch(cached, query)
            return cached, scores, True

        # Score all items
        scored = []
        for item in knowledge_items:
            score = self.scorer.score(item, query)
            if score >= min_relevance:
                scored.append((item, score))

        # Sort by score and limit
        scored.sort(key=lambda x: x[1], reverse=True)
        results = [item for item, _ in scored[:max_results]]
        scores = [score for _, score in scored[:max_results]]

        # Cache results
        self.cache.set(query, results)

        return results, scores, False


@dataclass
class SessionStartupConfig:
    """Configuration for session startup context loading."""

    max_critical_items: int = 10
    max_recent_items: int = 15
    recent_days: int = 7
    include_task_relevant: bool = True
    max_total_tokens: int = 2000
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_critical_items": self.max_critical_items,
            "max_recent_items": self.max_recent_items,
            "recent_days": self.recent_days,
            "include_task_relevant": self.include_task_relevant,
            "max_total_tokens": self.max_total_tokens,
            "strategy": self.strategy.value,
        }


class RetrievalOptimizer:
    """Main class for optimizing knowledge retrieval."""

    def __init__(
        self,
        knowledge_store_path: Path | None = None,
        cache_size: int = 100,
    ):
        """Initialize optimizer."""
        self.proactive_loader = ProactiveLoader(knowledge_store_path)
        self.cache = RetrievalCache(max_size=cache_size)
        self.reactive_retriever = ReactiveRetriever(self.cache)
        self.task_detector = TaskTypeDetector()
        self.scorer = RelevanceScorer()
        self.metrics = RetrievalMetrics()
        self._loaded = False

    def initialize(self) -> int:
        """Initialize by loading knowledge store."""
        items = self.proactive_loader.load_knowledge_store()
        self._loaded = True
        return len(items)

    def get_session_startup_context(
        self,
        task_hint: str | None = None,
        config: SessionStartupConfig | None = None,
    ) -> dict[str, Any]:
        """Get optimized context for session startup."""
        import time

        start_time = time.time()
        config = config or SessionStartupConfig()

        if not self._loaded:
            self.initialize()

        result: dict[str, Any] = {
            "critical": [],
            "recent": [],
            "task_relevant": [],
            "strategy": config.strategy.value,
        }

        # Always include critical knowledge
        critical = self.proactive_loader.get_critical_knowledge()
        result["critical"] = critical[: config.max_critical_items]

        # Include recent knowledge
        recent = self.proactive_loader.get_recent_knowledge(config.recent_days)
        result["recent"] = recent[: config.max_recent_items]

        # Include task-relevant knowledge if hint provided
        if task_hint and config.include_task_relevant:
            task_type = self.task_detector.detect(task_hint)
            if task_type != TaskType.UNKNOWN:
                task_items = self.proactive_loader.get_task_relevant_knowledge(task_type)
                result["task_relevant"] = task_items[:10]
                result["detected_task_type"] = task_type.value

        elapsed_ms = (time.time() - start_time) * 1000
        result["load_time_ms"] = elapsed_ms

        return result

    def retrieve(
        self,
        query: str,
        max_results: int = 10,
        min_relevance: float = 0.1,
    ) -> RetrievalResult:
        """Retrieve relevant knowledge for a query."""
        import time

        start_time = time.time()

        if not self._loaded:
            self.initialize()

        items, scores, cache_hit = self.reactive_retriever.retrieve(
            query,
            self.proactive_loader._knowledge_cache,
            max_results=max_results,
            min_relevance=min_relevance,
        )

        elapsed_ms = (time.time() - start_time) * 1000

        result = RetrievalResult(
            query=query,
            items=items,
            retrieval_time_ms=elapsed_ms,
            strategy_used=RetrievalStrategy.REACTIVE,
            cache_hit=cache_hit,
            relevance_scores=scores,
        )

        self.metrics.record(result)
        return result

    def expand_context(
        self,
        current_context: str,
        expansion_query: str,
        max_additions: int = 5,
    ) -> list[dict[str, Any]]:
        """Expand context when agent is stuck."""
        # Combine current context and query for better matching
        combined_query = f"{current_context} {expansion_query}"

        result = self.retrieve(
            combined_query,
            max_results=max_additions,
            min_relevance=0.05,  # Lower threshold for expansion
        )

        return result.items

    def get_similar_sessions(
        self,
        session_context: str,
        max_results: int = 3,
    ) -> list[dict[str, Any]]:
        """Find similar past sessions."""
        result = self.retrieve(
            session_context,
            max_results=max_results * 2,  # Get more to filter
            min_relevance=0.2,
        )

        # Group by session and return session summaries
        sessions: dict[str, list[dict[str, Any]]] = {}
        for item in result.items:
            session_id = item.get("session_id", "unknown")
            sessions.setdefault(session_id, []).append(item)

        # Return sessions with most matches
        session_scores = [(sid, len(items), items) for sid, items in sessions.items()]
        session_scores.sort(key=lambda x: x[1], reverse=True)

        return [
            {"session_id": sid, "match_count": count, "sample_items": items[:3]}
            for sid, count, items in session_scores[:max_results]
        ]

    def get_metrics(self) -> dict[str, Any]:
        """Get retrieval metrics."""
        return self.metrics.to_dict()

    def clear_cache(self) -> None:
        """Clear the retrieval cache."""
        self.cache.clear()

    def warm_cache(self, common_queries: list[str]) -> int:
        """Warm the cache with common queries."""
        warmed = 0
        for query in common_queries:
            self.retrieve(query)
            warmed += 1
        return warmed
