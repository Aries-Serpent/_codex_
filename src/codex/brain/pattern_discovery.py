"""
Pattern Discovery System

Identifies, classifies, and scores recurring patterns in memory
for promotion to long-term storage.

PHASE 10.2: Pattern Discovery & Promotion
Status: Production Ready
"""

import json
import logging
import math
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Pattern type enumeration."""

    DECISION = "decision"
    ERROR = "error"
    PERFORMANCE = "performance"
    SUCCESS = "success"
    RISK = "risk"


class ImprovementArea(Enum):
    """Categories for improvement tracking."""

    ML_PATTERN_FEEDING = "ML_PATTERN_FEEDING"
    CI_SELF_HEALING = "CI_SELF_HEALING"
    AGENT_CHAINING = "AGENT_CHAINING"
    COVERAGE_IMPROVEMENT = "COVERAGE_IMPROVEMENT"
    PERFORMANCE_OPTIMIZATION = "PERFORMANCE_OPTIMIZATION"
    SECURITY_HARDENING = "SECURITY_HARDENING"
    ERROR_RESILIENCE = "ERROR_RESILIENCE"


@dataclass
class Pattern:
    """Represents a discovered pattern."""

    id: str
    name: str
    pattern_type: PatternType
    description: str
    frequency: int = 1
    success_rate: float = 0.5
    confidence: float = 0.0
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    occurrences: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    improvement_areas: list[ImprovementArea] = field(default_factory=list)


@dataclass
class PatternOccurrence:
    """A single occurrence of a pattern."""

    timestamp: datetime
    context: dict[str, Any]
    outcome: Optional[str] = None  # success, failure, neutral
    metadata: dict[str, Any] = field(default_factory=dict)


class PatternClassifier:
    """Classifies events into pattern types."""

    # Keywords for pattern type detection
    TYPE_KEYWORDS = {
        PatternType.DECISION: ["choose", "select", "decision", "branch", "option", "algorithm"],
        PatternType.ERROR: ["error", "exception", "fail", "timeout", "crash", "bug"],
        PatternType.PERFORMANCE: ["latency", "throughput", "memory", "cpu", "speed", "benchmark"],
        PatternType.SUCCESS: ["success", "pass", "completed", "accomplished", "resolved"],
        PatternType.RISK: ["risk", "vulnerability", "security", "dangerous", "critical"],
    }

    @staticmethod
    def classify(event: dict[str, Any]) -> PatternType:
        """Classify an event into a pattern type."""
        event_str = json.dumps(event).lower()

        # Check for pattern type keywords
        for ptype, keywords in PatternClassifier.TYPE_KEYWORDS.items():
            if any(kw in event_str for kw in keywords):
                return ptype

        # Default to success if outcome is successful
        if event.get("outcome") == "success":
            return PatternType.SUCCESS
        elif event.get("outcome") == "failure":
            return PatternType.ERROR

        # Default classification
        return PatternType.DECISION


class PatternScorer:
    """Scores patterns for importance and promotion."""

    @staticmethod
    def calculate_score(pattern: Pattern, now: Optional[datetime] = None) -> float:
        """
        Calculate pattern score.

        Score = (Frequency × Recency × Success_Rate) / Age_Decay
        Range: 0.0 - 1.0
        """
        if now is None:
            now = datetime.now(timezone.utc)

        # Frequency component
        frequency_score = min(pattern.frequency / 5, 1.0)  # Normalize to 5+

        # Recency component (exponential decay)
        days_since_seen = (now - pattern.last_seen).total_seconds() / 86400
        recency_score = math.exp(-(days_since_seen / 30))

        # Success rate component
        success_score = pattern.success_rate

        # Age decay (older patterns less valuable)
        days_since_creation = (now - pattern.first_seen).total_seconds() / 86400
        age_decay = math.exp(days_since_creation / 90)

        # Combined score
        score = (frequency_score * recency_score * success_score) / age_decay
        return min(score, 1.0)

    @staticmethod
    def calculate_confidence(pattern: Pattern, frequency_threshold: int = 3) -> float:
        """
        Calculate confidence in pattern promotion.

        Components:
        - Frequency confidence
        - Success rate confidence
        - Consistency confidence
        """
        # Frequency confidence (0.0-0.4)
        freq_conf = min(pattern.frequency / frequency_threshold, 1.0) * 0.4

        # Success rate confidence (0.0-0.4)
        success_conf = pattern.success_rate * 0.4

        # Consistency confidence (0.0-0.2)
        if pattern.occurrences:
            # Variance in outcomes
            outcomes = [o.outcome for o in pattern.occurrences if o.outcome]  # type: ignore[attr-defined]
            if outcomes:
                outcome_counts = Counter(outcomes)
                max_count = max(outcome_counts.values())
                consistency = max_count / len(outcomes)
                consistency_conf = consistency * 0.2
            else:
                consistency_conf = 0.1
        else:
            consistency_conf = 0.0

        confidence = freq_conf + success_conf + consistency_conf
        return min(confidence, 1.0)


class TaggingEngine:
    """Tags patterns with improvement areas based on content."""

    IMPROVEMENT_KEYWORDS = {
        ImprovementArea.ML_PATTERN_FEEDING: ["stm", "ltm", "memory", "consolidat", "pattern"],
        ImprovementArea.CI_SELF_HEALING: ["ci", "fail", "heal", "self-heal", "error"],
        ImprovementArea.AGENT_CHAINING: ["agent", "chain", "orchestrat", "workflow"],
        ImprovementArea.COVERAGE_IMPROVEMENT: ["coverage", "test", "gap"],
        ImprovementArea.PERFORMANCE_OPTIMIZATION: [
            "latency",
            "throughput",
            "performance",
            "optimize",
        ],
        ImprovementArea.SECURITY_HARDENING: ["security", "vulnerability", "secret", "auth"],
        ImprovementArea.ERROR_RESILIENCE: ["error", "recovery", "resilience", "fault"],
    }

    @staticmethod
    def tag_pattern(pattern: Pattern) -> list[str]:
        """Generate tags for a pattern."""
        content = f"{pattern.name} {pattern.description}".lower()
        tags = []

        for area, keywords in TaggingEngine.IMPROVEMENT_KEYWORDS.items():
            if any(kw in content for kw in keywords):
                tags.append(area.value)
                if area not in pattern.improvement_areas:
                    pattern.improvement_areas.append(area)

        return tags


class PatternDiscovery:
    """
    Main pattern discovery engine.

    Identifies recurring patterns in events, classifies them,
    and scores them for promotion to long-term memory.
    """

    def __init__(self, frequency_threshold: int = 3):
        """Initialize pattern discovery."""
        self.frequency_threshold = frequency_threshold
        self.patterns: dict[str, Pattern] = {}
        self.event_sequences: list[dict[str, Any]] = []
        self.classifier = PatternClassifier()
        self.scorer = PatternScorer()
        self.tagger = TaggingEngine()

    def add_event(self, event: dict[str, Any]) -> None:
        """Add an event for pattern analysis."""
        self.event_sequences.append(event)

    def discover(self, events: Optional[list[dict[str, Any]]] = None) -> list[Pattern]:
        """
        Discover patterns from events.

        Returns:
            List of discovered patterns sorted by score
        """
        if events:
            self.event_sequences = events

        if not self.event_sequences:
            return []

        # Analyze events
        self._analyze_events()

        # Score patterns
        now = datetime.now(timezone.utc)
        scored_patterns = []

        for pattern in self.patterns.values():
            score = self.scorer.calculate_score(pattern, now)
            confidence = self.scorer.calculate_confidence(pattern, self.frequency_threshold)
            pattern.confidence = confidence

            if pattern.frequency >= self.frequency_threshold:
                scored_patterns.append((pattern, score))

        # Sort by score descending
        scored_patterns.sort(key=lambda x: x[1], reverse=True)

        discovered = [p for p, _ in scored_patterns]
        logger.info(f"Discovered {len(discovered)} patterns")

        return discovered

    def _analyze_events(self) -> None:
        """Analyze event sequences to identify patterns."""
        event_groups = defaultdict(list)

        # Group events by type
        for event in self.event_sequences:
            ptype = self.classifier.classify(event)
            event_key = self._generate_event_key(event, ptype)
            event_groups[event_key].append(event)

        # Create patterns from groups
        for event_key, events in event_groups.items():
            if len(events) >= 1:
                self._create_pattern(event_key, events)

    def _generate_event_key(self, event: dict[str, Any], ptype: PatternType) -> str:
        """Generate a unique key for similar events."""
        # Normalize event for grouping
        key_parts = [ptype.value]

        # Extract relevant fields
        if "action" in event:
            key_parts.append(str(event["action"]))
        if "resource" in event:
            key_parts.append(str(event["resource"]))

        return "|".join(key_parts)

    def _create_pattern(self, event_key: str, events: list[dict[str, Any]]) -> None:
        """Create or update a pattern from grouped events."""
        if event_key not in self.patterns:
            # New pattern
            ptype = self.classifier.classify(events[0])
            pattern_id = f"{ptype.value}_{len(self.patterns)}"

            pattern = Pattern(
                id=pattern_id,
                name=self._generate_pattern_name(events[0], ptype),
                pattern_type=ptype,
                description=self._generate_pattern_description(events, ptype),
                frequency=len(events),
                success_rate=self._calculate_success_rate(events),
                first_seen=datetime.now(timezone.utc),
            )

            self.patterns[event_key] = pattern
        else:
            # Update existing pattern
            pattern = self.patterns[event_key]
            pattern.frequency += len(events)
            pattern.last_seen = datetime.now(timezone.utc)
            pattern.success_rate = self._calculate_success_rate(pattern.occurrences + events)

        # Add occurrences
        pattern = self.patterns[event_key]
        for event in events:
            occurrence = PatternOccurrence(
                timestamp=datetime.now(timezone.utc),
                context=event,
                outcome=event.get("outcome"),
                metadata=event.get("metadata", {}),
            )
            pattern.occurrences.append(occurrence)  # type: ignore[arg-type]

        # Tag pattern
        pattern.tags = self.tagger.tag_pattern(pattern)

    def _generate_pattern_name(self, event: dict[str, Any], ptype: PatternType) -> str:
        """Generate a descriptive name for a pattern."""
        if "name" in event:
            return event["name"]

        action = event.get("action", "event")
        resource = event.get("resource", "resource")
        return f"{action}_{resource}_{ptype.value}"

    def _generate_pattern_description(
        self, events: list[dict[str, Any]], ptype: PatternType
    ) -> str:
        """Generate a description for a pattern."""
        freq = len(events)
        success_rate = self._calculate_success_rate(events)

        return (
            f"Recurring {ptype.value} pattern observed {freq} times "
            f"with {success_rate * 100:.1f}% success rate"
        )

    def _calculate_success_rate(self, events: list[dict[str, Any]]) -> float:
        """Calculate success rate from events."""
        if not events:
            return 0.5

        successes = sum(1 for e in events if e.get("outcome") == "success")

        return successes / len(events)

    def get_promoted_patterns(self, score_threshold: float = 0.60) -> list[Pattern]:
        """Get patterns ready for promotion to LTM."""
        candidates = []
        now = datetime.now(timezone.utc)

        for pattern in self.patterns.values():
            score = self.scorer.calculate_score(pattern, now)

            if pattern.frequency >= self.frequency_threshold and score >= score_threshold:
                candidates.append(pattern)

        # Sort by score descending
        candidates.sort(key=lambda p: self.scorer.calculate_score(p, now), reverse=True)

        return candidates

    def export_patterns(self) -> dict[str, Any]:
        """Export discovered patterns as JSON."""
        return {
            "discovery_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_patterns": len(self.patterns),
            "patterns": [asdict(p) for p in self.patterns.values()],
        }


class MetricsCalculator:
    """Calculates metrics for discovered patterns."""

    @staticmethod
    def calculate_pattern_metrics(pattern: Pattern) -> dict[str, Any]:
        """Calculate metrics for a pattern."""
        outcomes = [o.outcome for o in pattern.occurrences if o.outcome]  # type: ignore[attr-defined]
        outcome_counts = Counter(outcomes) if outcomes else Counter()

        return {
            "frequency": pattern.frequency,
            "success_rate": pattern.success_rate,
            "confidence": pattern.confidence,
            "days_active": (
                (pattern.last_seen - pattern.first_seen).total_seconds() / 86400
                if pattern.occurrences
                else 0
            ),
            "outcome_distribution": dict(outcome_counts),
            "unique_contexts": len(
                {json.dumps(o.context, sort_keys=True) for o in pattern.occurrences}  # type: ignore[attr-defined]
            ),
        }

    @staticmethod
    def calculate_discovery_metrics(patterns: list[Pattern]) -> dict[str, Any]:
        """Calculate overall discovery metrics."""
        if not patterns:
            return {
                "total_patterns": 0,
                "average_confidence": 0.0,
                "average_frequency": 0.0,
                "type_distribution": {},
            }

        type_counts = Counter(p.pattern_type.value for p in patterns)

        return {
            "total_patterns": len(patterns),
            "average_confidence": sum(p.confidence for p in patterns) / len(patterns),
            "average_frequency": sum(p.frequency for p in patterns) / len(patterns),
            "average_success_rate": sum(p.success_rate for p in patterns) / len(patterns),
            "type_distribution": dict(type_counts),
            "improvement_areas": list(
                {area.value for p in patterns for area in p.improvement_areas}
            ),
        }
