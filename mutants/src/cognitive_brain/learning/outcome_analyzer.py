"""
Outcome Analyzer for Adaptive Learning.

Analyzes decision outcomes from the AfterMath feedback system to extract
learnings, identify patterns, and calculate reward signals for RL algorithms.

AfterMath: Phase 8.3 - Adaptive Learning Engine
PDA: Active - Continuous outcome analysis and pattern extraction
"""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional

from cognitive_brain.models.learning_outcome import (
    DecisionContext,
    LearningOutcome,
    OutcomeType,
    Pattern,
    PatternCategory,
    PatternSet,
)

logger = logging.getLogger(__name__)


class OutcomeAnalyzer:
    """
    Analyze decision outcomes and extract learnings.

    Integrates with AfterMath feedback system to continuously improve
    decision-making strategies through pattern detection and reward calculation.

    PDA Loop:
        - [PLAN] Design outcome analysis strategy
        - [DO] Extract patterns and calculate rewards
        - [AFTERMATH] Track learning improvements over time

    Attributes:
        outcomes: Stored learning outcomes
        patterns: Identified patterns
        reward_history: Historical reward signals
    """

    def __init__(self):
        """Initialize outcome analyzer."""
        self.outcomes: dict[str, LearningOutcome] = {}
        self.patterns: dict[str, Pattern] = {}
        self.reward_history: list[float] = []
        self.pattern_extraction_count = 0

        logger.info("OutcomeAnalyzer initialized")

    def analyze_outcome(
        self,
        decision_id: str,
        outcome_type: OutcomeType,
        result_metrics: dict[str, float],
        context: DecisionContext,
        outcome_id: Optional[str] = None,
    ) -> LearningOutcome:
        """
        Analyze a decision outcome and extract learnings.

        Args:
            decision_id: ID of decision that was made
            outcome_type: Type of outcome (success/failure/etc)
            result_metrics: Quantitative results (e.g., accuracy, latency)
            context: Context in which decision was made
            outcome_id: Optional custom outcome ID

        Returns:
            LearningOutcome object with extracted learnings

        PDA: [PLAN] Validate inputs → [DO] Extract patterns → [AFTERMATH] Calculate reward
        """
        # Generate outcome ID if not provided
        if outcome_id is None:
            outcome_id = f"outcome_{len(self.outcomes) + 1}"

        # Calculate reward signal
        reward = self._calculate_reward(outcome_type, result_metrics, context)

        # Identify patterns
        patterns_identified = self._identify_patterns(outcome_type, result_metrics, context)

        # Extract lessons
        lessons_learned = self._extract_lessons(
            outcome_type, result_metrics, context, patterns_identified
        )

        # Create learning outcome
        learning_outcome = LearningOutcome(
            outcome_id=outcome_id,
            decision_id=decision_id,
            outcome_type=outcome_type,
            reward=reward,
            context=context,
            result_metrics=result_metrics,
            patterns_identified=patterns_identified,
            lessons_learned=lessons_learned,
            timestamp=datetime.now(timezone.utc),
        )

        # Store outcome
        self.outcomes[outcome_id] = learning_outcome
        self.reward_history.append(reward)

        logger.info(
            f"Analyzed outcome '{outcome_id}': type={outcome_type.value}, "
            f"reward={reward:.3f}, patterns={len(patterns_identified)}"
        )

        return learning_outcome

    def _calculate_reward(
        self,
        outcome_type: OutcomeType,
        result_metrics: dict[str, float],
        context: DecisionContext,
    ) -> float:
        """
        Calculate reward signal for RL algorithms.

        Formula:
            R = base_reward × efficiency × (1 - time_penalty) + complexity_bonus

        where:
            - base_reward: +1.0 (success), -1.0 (failure), 0.5 (partial)
            - efficiency: result quality metric (0-1)
            - time_penalty: context.time_pressure adjusted (max 20%)
            - complexity_bonus: context.complexity adjusted (max 10%)

        Returns:
            Reward in [-1, +1]
        """
        # Base reward by outcome type
        base_rewards = {
            OutcomeType.SUCCESS: 1.0,
            OutcomeType.FAILURE: -1.0,
            OutcomeType.PARTIAL: 0.5,
            OutcomeType.TIMEOUT: -0.5,
            OutcomeType.ERROR: -0.8,
        }
        base_reward = base_rewards.get(outcome_type, 0.0)

        # Efficiency factor from metrics
        efficiency = result_metrics.get("efficiency", 1.0 if base_reward > 0 else 0.0)
        efficiency = max(0.0, min(1.0, efficiency))  # Clamp to [0,1]

        # For negative base rewards with zero efficiency, use minimum efficiency
        if base_reward < 0 and efficiency == 0.0:
            efficiency = 0.1  # Minimum efficiency to ensure negative reward propagates

        # Time penalty based on time pressure
        time_penalty = context.time_pressure * 0.2  # Max 20% penalty

        # Complexity bonus for harder tasks (only for positive outcomes)
        complexity_bonus = 0.0
        if base_reward > 0:
            complexity_bonus = context.complexity * 0.1  # Max 10% bonus

        # Calculate final reward
        reward = base_reward * efficiency * (1 - time_penalty) + complexity_bonus

        # Clamp to [-1, +1]
        return max(-1.0, min(1.0, reward))

    def _identify_patterns(
        self,
        outcome_type: OutcomeType,
        result_metrics: dict[str, float],
        context: DecisionContext,
    ) -> list[str]:
        """
        Identify patterns in the outcome.

        Detects 4 pattern categories:
        - TEMPORAL: Time-based patterns
        - CONTEXTUAL: Context-dependent patterns
        - SEQUENTIAL: Action sequence patterns
        - CAUSAL: Cause-effect patterns

        Note: Multiple patterns from different categories may be identified
        for the same outcome. This is intentional to capture all relevant
        dimensions of the decision outcome for comprehensive learning.

        Returns:
            List of pattern IDs
        """
        identified_patterns = []

        # Always identify at least one pattern based on outcome type and metrics
        # This ensures pattern detection is never empty for analysis

        # Temporal pattern: Time-of-day effects
        hour = datetime.now(timezone.utc).hour
        if outcome_type == OutcomeType.SUCCESS and 9 <= hour <= 17:
            identified_patterns.append("temporal_business_hours_success")
        elif outcome_type == OutcomeType.FAILURE and (hour < 6 or hour > 22):
            identified_patterns.append("temporal_off_hours_failure")

        # Contextual pattern: Complexity-based
        if context.complexity > 0.7 and outcome_type == OutcomeType.SUCCESS:
            identified_patterns.append("contextual_high_complexity_success")
        elif context.complexity < 0.3 and outcome_type == OutcomeType.FAILURE:
            identified_patterns.append("contextual_low_complexity_failure")
        elif 0.3 <= context.complexity <= 0.7:
            # Medium complexity - always add a pattern
            if outcome_type == OutcomeType.SUCCESS:
                identified_patterns.append("contextual_medium_complexity_success")
            else:
                identified_patterns.append("contextual_medium_complexity_failure")

        # Sequential pattern: Multi-agent coordination
        if len(context.agent_ids) > 2 and outcome_type == OutcomeType.SUCCESS:
            identified_patterns.append("sequential_multi_agent_success")
        elif len(context.agent_ids) == 1 and outcome_type == OutcomeType.FAILURE:
            identified_patterns.append("sequential_single_agent_failure")
        elif len(context.agent_ids) == 1 and outcome_type == OutcomeType.SUCCESS:
            identified_patterns.append("sequential_single_agent_success")

        # Causal pattern: Resource constraints
        if context.resource_constraints.get("cpu", 1.0) < 0.5:
            if outcome_type == OutcomeType.SUCCESS:
                identified_patterns.append("causal_low_resource_success")
            else:
                identified_patterns.append("causal_low_resource_failure")
        elif context.resource_constraints.get("cpu", 1.0) >= 0.5:
            # Normal resources - add pattern
            if outcome_type == OutcomeType.SUCCESS:
                identified_patterns.append("causal_normal_resource_success")

        # Causal pattern: High memory with success
        if context.resource_constraints.get("memory", 0.0) > 0.8:
            if outcome_type == OutcomeType.SUCCESS:
                identified_patterns.append("causal_high_memory_success")

        # Efficiency-based pattern (always detectable from metrics)
        efficiency = result_metrics.get("efficiency", 0.5)
        if efficiency > 0.8 and outcome_type == OutcomeType.SUCCESS:
            identified_patterns.append("performance_high_efficiency")
        elif efficiency < 0.3:
            identified_patterns.append("performance_low_efficiency")

        return identified_patterns

    def _extract_lessons(
        self,
        outcome_type: OutcomeType,
        result_metrics: dict[str, float],
        context: DecisionContext,
        patterns: list[str],
    ) -> list[str]:
        """
        Extract actionable lessons from the outcome.

        Returns:
            List of lesson strings
        """
        lessons = []

        if outcome_type == OutcomeType.SUCCESS:
            lessons.append(f"Strategy effective for {context.task_type}")
            if context.complexity > 0.7:
                lessons.append("Can handle high-complexity tasks successfully")
            if result_metrics.get("efficiency", 0) > 0.9:
                lessons.append("High efficiency achieved - consider reusing this strategy")
        elif outcome_type == OutcomeType.FAILURE:
            lessons.append(f"Strategy ineffective for {context.task_type}")
            if context.time_pressure > 0.8:
                lessons.append("High time pressure may have contributed to failure")
            if context.complexity > 0.8:
                lessons.append("Task complexity exceeded capability - need better decomposition")

        # Pattern-based lessons
        if "multi_agent_success" in str(patterns):
            lessons.append("Multi-agent coordination is beneficial")
        if "low_resource_failure" in str(patterns):
            lessons.append("Need better resource allocation strategy")
        if "high_complexity_success" in str(patterns):
            lessons.append("Complex problem solving capability confirmed")

        return lessons

    def identify_patterns(self, lookback_window: int = 100) -> PatternSet:
        """
        Find recurring success/failure patterns across recent outcomes.

        Args:
            lookback_window: Number of recent outcomes to analyze

        Returns:
            PatternSet with identified patterns

        PDA: [PLAN] Define search space → [DO] Extract patterns → [AFTERMATH] Validate
        """
        recent_outcomes = list(self.outcomes.values())[-lookback_window:]

        if not recent_outcomes:
            return PatternSet(patterns=[], domain="general")

        # Track pattern occurrences
        pattern_counts: defaultdict[str, int] = defaultdict(int)
        pattern_examples: defaultdict[str, list[Any]] = defaultdict(list)

        for outcome in recent_outcomes:
            for pattern_id in outcome.patterns_identified:
                pattern_counts[pattern_id] += 1
                pattern_examples[pattern_id].append(outcome.outcome_id)

        # Create Pattern objects
        patterns = []
        for pattern_id, count in pattern_counts.items():
            # Determine category from pattern ID
            if "temporal" in pattern_id:
                category = PatternCategory.TEMPORAL
            elif "contextual" in pattern_id:
                category = PatternCategory.CONTEXTUAL
            elif "sequential" in pattern_id:
                category = PatternCategory.SEQUENTIAL
            else:
                category = PatternCategory.CAUSAL

            # Calculate confidence based on support
            confidence = min(1.0, count / lookback_window * 2)

            pattern = Pattern(
                pattern_id=pattern_id,
                category=category,
                description=pattern_id.replace("_", " ").title(),
                confidence=confidence,
                support_count=count,
                examples=pattern_examples[pattern_id][:5],  # Top 5 examples
            )
            patterns.append(pattern)

        self.pattern_extraction_count += 1

        pattern_set = PatternSet(
            patterns=patterns,
            domain="cognitive_brain",
            extraction_date=datetime.now(timezone.utc),
            statistics={
                "total_patterns": len(patterns),
                "outcomes_analyzed": len(recent_outcomes),
                "extraction_number": self.pattern_extraction_count,
            },
        )

        # Store patterns
        for pattern in patterns:
            self.patterns[pattern.pattern_id] = pattern

        logger.info(f"Extracted {len(patterns)} patterns from {len(recent_outcomes)} outcomes")

        return pattern_set

    def get_statistics(self) -> dict[str, Any]:
        """
        Get analyzer statistics.

        Returns:
            Dictionary with outcomes analyzed, patterns identified, avg reward
        """
        avg_reward = (
            sum(self.reward_history) / len(self.reward_history) if self.reward_history else 0.0
        )

        success_count = sum(
            1 for o in self.outcomes.values() if o.outcome_type == OutcomeType.SUCCESS
        )

        return {
            "outcomes_analyzed": len(self.outcomes),
            "patterns_identified": len(self.patterns),
            "pattern_extractions": self.pattern_extraction_count,
            "average_reward": avg_reward,
            "success_rate": success_count / len(self.outcomes) if self.outcomes else 0.0,
        }
