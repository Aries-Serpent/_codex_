"""
Learning Outcome Data Models.

Structures for capturing and analyzing decision outcomes in the cognitive brain.
Integrates with AfterMath feedback system for continuous improvement.

AfterMath: Phase 8.3 - Adaptive Learning Engine
PDA: Active - Outcome tracking and pattern extraction
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class OutcomeType(Enum):
    """Types of decision outcomes."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    ERROR = "error"


class PatternCategory(Enum):
    """Categories of identified patterns."""

    TEMPORAL = "temporal"  # Time-based patterns
    CONTEXTUAL = "contextual"  # Context-dependent patterns
    SEQUENTIAL = "sequential"  # Action sequence patterns
    CAUSAL = "causal"  # Cause-effect patterns


@dataclass
class DecisionContext:
    """
    Context in which a decision was made.

    Attributes:
        task_type: Type of task being solved
        complexity: Estimated complexity (0-1)
        resource_constraints: Available resources
        time_pressure: Time pressure level (0-1)
        agent_ids: Agents involved in decision
        metadata: Additional contextual information
    """

    task_type: str
    complexity: float
    resource_constraints: dict[str, float]
    time_pressure: float = 0.5
    agent_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate decision context."""
        if not 0.0 <= self.complexity <= 1.0:
            raise ValueError(f"Complexity must be in [0,1], got {self.complexity}")
        if not 0.0 <= self.time_pressure <= 1.0:
            raise ValueError(f"Time pressure must be in [0,1], got {self.time_pressure}")


@dataclass
class LearningOutcome:
    """
    Structured outcome of a decision for learning purposes.

    Attributes:
        outcome_id: Unique identifier
        decision_id: Associated decision ID
        outcome_type: Type of outcome (success/failure/etc)
        reward: Reward signal for RL (-1 to +1)
        context: Decision context
        result_metrics: Quantitative metrics
        patterns_identified: Detected patterns
        lessons_learned: Extracted lessons
        timestamp: When outcome was recorded

    PDA: [DATA] Learning outcome container for adaptive algorithms
    """

    outcome_id: str
    decision_id: str
    outcome_type: OutcomeType
    reward: float
    context: DecisionContext
    result_metrics: dict[str, float] = field(default_factory=dict)
    patterns_identified: list[str] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate learning outcome."""
        if not -1.0 <= self.reward <= 1.0:
            raise ValueError(f"Reward must be in [-1,1], got {self.reward}")
        if not self.outcome_id:
            raise ValueError("outcome_id cannot be empty")
        if not self.decision_id:
            raise ValueError("decision_id cannot be empty")


@dataclass
class Pattern:
    """
    Identified pattern in decision-making.

    Attributes:
        pattern_id: Unique identifier
        category: Pattern category
        description: Human-readable description
        confidence: Confidence in pattern (0-1)
        support_count: Number of occurrences
        examples: Example instances
        applicability: When pattern applies
    """

    pattern_id: str
    category: PatternCategory
    description: str
    confidence: float
    support_count: int = 0
    examples: list[str] = field(default_factory=list)
    applicability: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate pattern."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0,1], got {self.confidence}")
        if self.support_count < 0:
            raise ValueError(f"Support count cannot be negative: {self.support_count}")


@dataclass
class PatternSet:
    """
    Collection of related patterns.

    Attributes:
        patterns: List of patterns
        domain: Problem domain
        extraction_date: When patterns were extracted
        statistics: Pattern set statistics
    """

    patterns: list[Pattern]
    domain: str
    extraction_date: datetime = field(default_factory=datetime.now)
    statistics: dict[str, Any] = field(default_factory=dict)

    def get_by_category(self, category: PatternCategory) -> list[Pattern]:
        """Get patterns by category."""
        return [p for p in self.patterns if p.category == category]

    def get_high_confidence(self, threshold: float = 0.8) -> list[Pattern]:
        """Get high-confidence patterns."""
        return [p for p in self.patterns if p.confidence >= threshold]
