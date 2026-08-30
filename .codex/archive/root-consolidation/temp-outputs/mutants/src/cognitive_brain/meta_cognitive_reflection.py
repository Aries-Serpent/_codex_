"""
Meta-Cognitive Reflection Layer

Implements self-reflection and meta-cognitive capabilities for AI agents.
Enables agents to think about their own thinking processes.

Reference: .codex/docs/COGNITIVE_ARCHITECTURE.md#meta-memory
Philosophical Foundation: Meta-cognition and recursive self-awareness

Core Concepts:
- Meta-cognition: Thinking about thinking
- Self-monitoring: Tracking one's own cognitive processes
- Self-regulation: Adjusting strategies based on reflection
- Meta-memory: Knowledge about one's own memory and learning

This layer enables agents to:
1. Reflect on their decision-making processes
2. Evaluate the effectiveness of their strategies
3. Identify patterns in their own behavior
4. Adapt and improve their approaches
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

LOGGER = logging.getLogger(__name__)


class ReflectionType(Enum):
    """Types of meta-cognitive reflection."""

    DECISION = "decision"  # Reflecting on a decision made
    STRATEGY = "strategy"  # Reflecting on a strategy used
    OUTCOME = "outcome"  # Reflecting on an outcome achieved
    PATTERN = "pattern"  # Reflecting on a behavioral pattern
    ERROR = "error"  # Reflecting on an error made
    SUCCESS = "success"  # Reflecting on a success achieved


class QualityAssessment(Enum):
    """Quality assessments for reflections."""

    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    POOR = "poor"
    FAILED = "failed"


@dataclass
class Reflection:
    """
    A meta-cognitive reflection on an agent's own process.

    This is the agent thinking about its own thinking.
    """

    reflection_id: str
    reflection_type: ReflectionType
    subject: str  # What the reflection is about
    observation: str  # What was observed
    analysis: str  # Analysis of what happened
    learning: str  # What was learned
    quality: QualityAssessment
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            f"Reflection on {self.subject}: {self.observation[:50]}... "
            f"(Quality: {self.quality.value})"
        )


@dataclass
class StrategyPattern:
    """
    A pattern identified in an agent's strategy usage.

    Example: "When dealing with X, agent tends to use strategy Y"
    """

    pattern_id: str
    condition: str  # When does this pattern occur?
    behavior: str  # What does the agent do?
    effectiveness: float  # 0.0 (ineffective) to 1.0 (highly effective)
    occurrences: int = 0
    first_observed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_observed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MetaKnowledge:
    """
    Knowledge about knowledge - what the agent knows about what it knows.

    Example: "I know that my code generation is strong but my debugging is weak"
    """

    domain: str  # What area of knowledge
    strength_assessment: float  # 0.0 (weak) to 1.0 (strong)
    confidence: float  # 0.0 (uncertain) to 1.0 (certain)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evidence: list[str] = field(default_factory=list)


class MetaCognitiveReflectionLayer:
    """
    Meta-cognitive reflection layer for AI agents.

    Enables agents to reflect on their own processes, identify patterns,
    and adapt their strategies.

    Example:
        >>> layer = MetaCognitiveReflectionLayer("copilot-agent-1")
        >>> layer.reflect_on_decision(
        ...     subject="Code review approach",
        ...     observation="Used line-by-line review",
        ...     analysis="Caught 5 issues but took 20 minutes",
        ...     learning="Could use automated checks first",
        ...     quality=QualityAssessment.GOOD
        ... )
        >>> patterns = layer.identify_strategy_patterns()
        >>> print(f"Found {len(patterns)} patterns")
    """

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        self.reflections: list[Reflection] = []
        self.strategy_patterns: dict[str, StrategyPattern] = {}
        self.meta_knowledge: dict[str, MetaKnowledge] = {}
        LOGGER.info(f"MetaCognitiveReflectionLayer initialized for {agent_id}")

    def reflect(
        self,
        reflection_type: ReflectionType,
        subject: str,
        observation: str,
        analysis: str,
        learning: str,
        quality: QualityAssessment,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Reflection:
        """
        Create a reflection on a specific aspect of the agent's process.

        Args:
            reflection_type: Type of reflection
            subject: What the reflection is about
            observation: What was observed
            analysis: Analysis of what happened
            learning: What was learned
            quality: Quality assessment
            metadata: Optional metadata

        Returns:
            The created reflection
        """
        timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        reflection_id = f"{reflection_type.value}_{timestamp_ms}"

        reflection = Reflection(
            reflection_id=reflection_id,
            reflection_type=reflection_type,
            subject=subject,
            observation=observation,
            analysis=analysis,
            learning=learning,
            quality=quality,
            metadata=metadata or {},
        )

        self.reflections.append(reflection)

        LOGGER.info(
            f"Agent {self.agent_id} reflected on {subject} "
            f"(type: {reflection_type.value}, quality: {quality.value})"
        )

        return reflection

    def reflect_on_decision(
        self,
        subject: str,
        observation: str,
        analysis: str,
        learning: str,
        quality: QualityAssessment,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Reflection:
        """Convenience method for reflecting on a decision."""
        return self.reflect(
            ReflectionType.DECISION,
            subject,
            observation,
            analysis,
            learning,
            quality,
            metadata,
        )

    def reflect_on_error(
        self,
        subject: str,
        observation: str,
        analysis: str,
        learning: str,
        quality: QualityAssessment,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Reflection:
        """Convenience method for reflecting on an error."""
        return self.reflect(
            ReflectionType.ERROR,
            subject,
            observation,
            analysis,
            learning,
            quality,
            metadata,
        )

    def reflect_on_success(
        self,
        subject: str,
        observation: str,
        analysis: str,
        learning: str,
        quality: QualityAssessment,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Reflection:
        """Convenience method for reflecting on a success."""
        return self.reflect(
            ReflectionType.SUCCESS,
            subject,
            observation,
            analysis,
            learning,
            quality,
            metadata,
        )

    def record_strategy_pattern(
        self,
        pattern_id: str,
        condition: str,
        behavior: str,
        effectiveness: float,
    ) -> StrategyPattern:
        """
        Record a pattern in strategy usage.

        Args:
            pattern_id: Unique identifier for the pattern
            condition: When does this pattern occur?
            behavior: What does the agent do?
            effectiveness: How effective is this pattern? (0.0 to 1.0)

        Returns:
            The recorded pattern
        """
        if pattern_id in self.strategy_patterns:
            # Update existing pattern
            pattern = self.strategy_patterns[pattern_id]
            pattern.occurrences += 1
            pattern.last_observed = datetime.now(timezone.utc)
            pattern.effectiveness = (
                pattern.effectiveness * 0.7 + effectiveness * 0.3
            )  # Weighted average
        else:
            # Create new pattern
            pattern = StrategyPattern(
                pattern_id=pattern_id,
                condition=condition,
                behavior=behavior,
                effectiveness=effectiveness,
                occurrences=1,
            )
            self.strategy_patterns[pattern_id] = pattern

        LOGGER.debug(
            f"Recorded strategy pattern: {condition} -> {behavior} "
            f"(effectiveness: {pattern.effectiveness:.2%})"
        )

        return pattern

    def identify_strategy_patterns(self) -> list[StrategyPattern]:
        """
        Identify patterns in the agent's reflections.

        Analyzes past reflections to find recurring strategy patterns.

        Returns:
            List of identified patterns
        """
        # This is a simplified implementation
        # In a real system, this would use ML pattern recognition

        # Look for repeated subjects in reflections
        subject_counts: dict[str, list[Reflection]] = {}
        for reflection in self.reflections:
            subject = reflection.subject
            if subject not in subject_counts:
                subject_counts[subject] = []
            subject_counts[subject].append(reflection)

        # For subjects with multiple reflections, create patterns
        for subject, reflections_list in subject_counts.items():
            if len(reflections_list) >= 2:
                # Calculate average quality
                quality_scores = {
                    QualityAssessment.EXCELLENT: 1.0,
                    QualityAssessment.GOOD: 0.8,
                    QualityAssessment.ADEQUATE: 0.6,
                    QualityAssessment.POOR: 0.4,
                    QualityAssessment.FAILED: 0.2,
                }

                avg_effectiveness = sum(
                    quality_scores.get(r.quality, 0.5) for r in reflections_list
                ) / len(reflections_list)

                # Create or update pattern
                pattern_id = f"pattern_{subject.replace(' ', '_')}"
                self.record_strategy_pattern(
                    pattern_id=pattern_id,
                    condition=f"When working on {subject}",
                    behavior="Observed recurring approach",
                    effectiveness=avg_effectiveness,
                )

        return list(self.strategy_patterns.values())

    def update_meta_knowledge(
        self,
        domain: str,
        strength_assessment: float,
        confidence: float,
        evidence: Optional[list[str]] = None,
    ) -> MetaKnowledge:
        """
        Update meta-knowledge about a domain.

        Args:
            domain: Area of knowledge
            strength_assessment: How strong is the knowledge? (0.0 to 1.0)
            confidence: How confident in this assessment? (0.0 to 1.0)
            evidence: Evidence supporting this assessment

        Returns:
            Updated meta-knowledge
        """
        if domain in self.meta_knowledge:
            meta_k = self.meta_knowledge[domain]
            # Update with weighted average
            meta_k.strength_assessment = (
                meta_k.strength_assessment * 0.7 + strength_assessment * 0.3
            )
            meta_k.confidence = meta_k.confidence * 0.7 + confidence * 0.3
            if evidence:
                meta_k.evidence.extend(evidence)
            meta_k.last_updated = datetime.now(timezone.utc)
        else:
            meta_k = MetaKnowledge(
                domain=domain,
                strength_assessment=strength_assessment,
                confidence=confidence,
                evidence=evidence or [],
            )
            self.meta_knowledge[domain] = meta_k

        LOGGER.debug(
            f"Updated meta-knowledge for {domain}: "
            f"strength={meta_k.strength_assessment:.2%}, "
            f"confidence={meta_k.confidence:.2%}"
        )

        return meta_k

    def get_strengths(self, threshold: float = 0.7) -> list[MetaKnowledge]:
        """
        Get domains where the agent has strong knowledge.

        Args:
            threshold: Minimum strength threshold (0.0 to 1.0)

        Returns:
            List of strong domains
        """
        return [mk for mk in self.meta_knowledge.values() if mk.strength_assessment >= threshold]

    def get_weaknesses(self, threshold: float = 0.5) -> list[MetaKnowledge]:
        """
        Get domains where the agent has weak knowledge.

        Args:
            threshold: Maximum strength threshold (0.0 to 1.0)

        Returns:
            List of weak domains
        """
        return [mk for mk in self.meta_knowledge.values() if mk.strength_assessment < threshold]

    def generate_self_assessment_report(self) -> str:
        """
        Generate a self-assessment report.

        The agent reflects on its own capabilities and patterns.

        Returns:
            Formatted report string
        """
        lines = [
            "═" * 60,
            f"META-COGNITIVE SELF-ASSESSMENT: {self.agent_id}",
            "═" * 60,
            "",
            f"Total Reflections: {len(self.reflections)}",
            f"Identified Patterns: {len(self.strategy_patterns)}",
            "",
            "─" * 60,
            "STRENGTHS",
            "─" * 60,
        ]

        strengths = self.get_strengths()
        if strengths:
            for mk in strengths:
                lines.append(
                    f"✅ {mk.domain}: {mk.strength_assessment:.0%} "
                    f"(confidence: {mk.confidence:.0%})"
                )
        else:
            lines.append("No identified strengths yet")

        lines.extend(
            [
                "",
                "─" * 60,
                "AREAS FOR IMPROVEMENT",
                "─" * 60,
            ]
        )

        weaknesses = self.get_weaknesses()
        if weaknesses:
            for mk in weaknesses:
                lines.append(
                    f"⚠️  {mk.domain}: {mk.strength_assessment:.0%} "
                    f"(confidence: {mk.confidence:.0%})"
                )
        else:
            lines.append("No identified weaknesses")

        lines.extend(
            [
                "",
                "─" * 60,
                "EFFECTIVE STRATEGIES",
                "─" * 60,
            ]
        )

        effective_patterns = [p for p in self.strategy_patterns.values() if p.effectiveness >= 0.7]
        if effective_patterns:
            for pattern in effective_patterns:
                lines.append(
                    f"✅ {pattern.condition} → {pattern.behavior} "
                    f"({pattern.effectiveness:.0%} effective, "
                    f"{pattern.occurrences} uses)"
                )
        else:
            lines.append("No highly effective patterns identified yet")

        lines.extend(
            [
                "",
                "═" * 60,
            ]
        )

        return "\n".join(lines)

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about meta-cognitive reflections."""
        quality_counts: dict[str, Any] = {}
        for reflection in self.reflections:
            quality = reflection.quality.value
            quality_counts[quality] = quality_counts.get(quality, 0) + 1

        return {
            "agent_id": self.agent_id,
            "total_reflections": len(self.reflections),
            "reflections_by_quality": quality_counts,
            "identified_patterns": len(self.strategy_patterns),
            "meta_knowledge_domains": len(self.meta_knowledge),
            "known_strengths": len(self.get_strengths()),
            "known_weaknesses": len(self.get_weaknesses()),
        }
