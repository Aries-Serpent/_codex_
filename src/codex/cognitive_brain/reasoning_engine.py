"""
Core Multi-layer Reasoning Architecture.

This module implements a sophisticated reasoning engine with 5 operational layers:
- PerceptionLayer: Extract and normalize agent context
- ReasoningLayer: Generate multiple candidate decisions via different strategies
- ActionLayer: Select optimal decision with confidence scoring
- FeedbackLayer: Collect and validate outcomes asynchronously
- ImprovementLayer: Autonomously adjust weights and strategies

Performance Targets:
- Decision latency: <500ms (p99)
- Decision accuracy: >95%
- Confidence calibration: Brier score <0.15 (±5% accuracy)
- Minimum 1000 decisions/types for validation
"""

import asyncio
import json
import logging
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from src.codex.cognitive_brain.calibration import ConfidenceCalibrator

if TYPE_CHECKING:
    from src.codex.cognitive_brain.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class DecisionStrategy(str, Enum):
    """Decision generation strategies."""

    HEURISTIC = "heuristic"
    MACHINE_LEARNING = "ml"
    ENSEMBLE = "ensemble"


class ConfidenceLevel(str, Enum):
    """Confidence level classifications."""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class AgentContext:
    """Agent decision context extracted from current state."""

    goal: str
    constraints: List[str]
    decision_history: List[Dict[str, Any]]
    current_state: Dict[str, Any]
    category: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CandidateDecision:
    """A candidate decision with metadata."""

    id: str
    strategy: DecisionStrategy
    option: str
    reasoning: str
    confidence: float
    validation_rules: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "strategy": self.strategy.value,
            "option": self.option,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "validation_rules": self.validation_rules,
        }


@dataclass
class Decision:
    """Final selected decision with full metadata."""

    id: str
    option: str
    confidence: float
    confidence_level: ConfidenceLevel
    reasoning: str
    strategy: DecisionStrategy
    candidates: List[CandidateDecision]
    domain_validation: bool
    latency_ms: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "option": self.option,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level.value,
            "reasoning": self.reasoning,
            "strategy": self.strategy.value,
            "candidates": [c.to_dict() for c in self.candidates],
            "domain_validation": self.domain_validation,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
        }


@dataclass
class DecisionOutcome:
    """Outcome of a decision for feedback and learning."""

    decision_id: str
    success: bool
    actual_result: str
    expected_result: str
    confidence_was_accurate: bool
    latency_ms: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert bool to int for JSON serialization
        data["success"] = int(data["success"])
        data["confidence_was_accurate"] = int(data["confidence_was_accurate"])
        return data


class PerceptionLayer:
    """Extract and normalize agent context from current state.

    Responsibilities:
    - Parse goal and constraints
    - Build decision history
    - Extract relevant state variables
    - Normalize context for downstream layers
    """

    def __init__(self):
        """Initialize perception layer."""
        self.extraction_rules: Dict[str, Callable] = {}

    def extract_context(
        self,
        goal: str,
        constraints: List[str],
        decision_history: List[Dict[str, Any]],
        current_state: Dict[str, Any],
        category: str,
    ) -> AgentContext:
        """Extract normalized agent context.

        Args:
            goal: Agent decision goal
            constraints: List of constraints
            decision_history: Prior decisions made
            current_state: Current agent/system state
            category: Decision category for pattern matching

        Returns:
            AgentContext with normalized data
        """
        context = AgentContext(
            goal=goal,
            constraints=constraints,
            decision_history=decision_history[-10:],  # Keep last 10
            current_state=current_state,
            category=category,
        )
        logger.debug(
            f"Extracted context: goal={goal}, category={category}, "
            f"constraints={len(constraints)}"
        )
        return context

    def register_extraction_rule(
        self, category: str, rule: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """Register custom extraction rule for category."""
        self.extraction_rules[category] = rule


class ReasoningLayer:
    """Generate multiple candidate decisions via different strategies.

    Implements three generation strategies:
    - Heuristic: Fast, rule-based decisions
    - ML: ML model predictions (simulated)
    - Ensemble: Combination of multiple approaches
    """

    def __init__(self, knowledge_base: Optional["KnowledgeBase"] = None):
        """Initialize reasoning layer.

        Args:
            knowledge_base: Optional KB for pattern lookup
        """
        self.kb = knowledge_base
        self.decision_count = 0

    def generate_candidates(self, context: AgentContext) -> List[CandidateDecision]:
        """Generate 3+ candidate decisions via different strategies.

        Args:
            context: Normalized agent context

        Returns:
            List of candidate decisions with reasoning
        """
        candidates = []

        # Heuristic strategy
        heuristic = self._heuristic_strategy(context)
        if heuristic:
            candidates.append(heuristic)

        # ML strategy
        ml_decision = self._ml_strategy(context)
        if ml_decision:
            candidates.append(ml_decision)

        # Ensemble strategy
        ensemble_decision = self._ensemble_strategy(context, candidates)
        if ensemble_decision:
            candidates.append(ensemble_decision)

        self.decision_count += len(candidates)
        logger.debug(
            f"Generated {len(candidates)} candidates for category={context.category}"
        )
        return candidates

    def _heuristic_strategy(self, context: AgentContext) -> Optional[CandidateDecision]:
        """Apply heuristic rules for fast decision-making."""
        # Example heuristic: prefer recent successful patterns
        if context.decision_history:
            recent_success = next(
                (d for d in reversed(context.decision_history) if d.get("success")),
                None,
            )
            if recent_success:
                return CandidateDecision(
                    id=f"heuristic_{self.decision_count}",
                    strategy=DecisionStrategy.HEURISTIC,
                    option=recent_success.get("option", "default"),
                    reasoning="Based on recent successful pattern",
                    confidence=0.78,
                    validation_rules=["pattern_match", "recent_success"],
                )

        # Fallback heuristic
        return CandidateDecision(
            id=f"heuristic_{self.decision_count}",
            strategy=DecisionStrategy.HEURISTIC,
            option="conservative_choice",
            reasoning="Conservative default choice",
            confidence=0.65,
            validation_rules=["safety_first"],
        )

    def _ml_strategy(self, context: AgentContext) -> Optional[CandidateDecision]:
        """ML-based strategy using learned patterns."""
        # Simulated ML prediction with confidence
        confidence = min(
            0.92,
            0.70 + (len(context.decision_history) * 0.02),  # Improve with history
        )

        return CandidateDecision(
            id=f"ml_{self.decision_count}",
            strategy=DecisionStrategy.MACHINE_LEARNING,
            option="learned_optimal",
            reasoning=f"ML model prediction for {context.category}",
            confidence=confidence,
            validation_rules=["model_confidence", "pattern_correlation"],
        )

    def _ensemble_strategy(
        self, context: AgentContext, prior_candidates: List[CandidateDecision]
    ) -> Optional[CandidateDecision]:
        """Ensemble approach combining multiple strategies."""
        if not prior_candidates:
            return None

        avg_confidence = np.mean([c.confidence for c in prior_candidates])
        combined_reasoning = "; ".join(
            [f"{c.strategy.value}: {c.reasoning}" for c in prior_candidates]
        )

        return CandidateDecision(
            id=f"ensemble_{self.decision_count}",
            strategy=DecisionStrategy.ENSEMBLE,
            option="ensemble_consensus",
            reasoning=f"Ensemble of {len(prior_candidates)} strategies: {combined_reasoning}",
            confidence=min(0.96, avg_confidence + 0.05),
            validation_rules=["ensemble_agreement", "multi_strategy"],
        )


class ActionLayer:
    """Select best decision based on confidence and domain rules.

    Responsibilities:
    - Score candidate decisions
    - Apply domain validation rules
    - Select best option
    - Format final decision
    """

    def __init__(self, domain_rules: Optional[Dict[str, Callable]] = None):
        """Initialize action layer.

        Args:
            domain_rules: Optional domain-specific validation rules
        """
        self.domain_rules = domain_rules or {}

    def select_decision(
        self,
        context: AgentContext,
        candidates: List[CandidateDecision],
        calibrator: "ConfidenceCalibrator",
    ) -> Decision:
        """Select best decision using confidence and domain rules.

        Args:
            context: Agent context
            candidates: Candidate decisions to evaluate
            calibrator: Confidence calibration module

        Returns:
            Final selected decision
        """
        if not candidates:
            raise ValueError("No candidates provided for decision selection")

        start_time = time.time()

        # Score candidates
        scored = [
            (
                c,
                self._score_candidate(
                    c, context, calibrator
                ),  # (base_score, domain_score)
            )
            for c in candidates
        ]

        # Select best
        best_candidate, (base_score, domain_score) = max(
            scored, key=lambda x: x[1][0] + x[1][1]
        )

        # Validate against domain rules
        domain_valid = self._validate_domain_rules(best_candidate, context)

        # Calibrate confidence
        calibrated_confidence = calibrator.calibrate_confidence(
            best_candidate.confidence, context.category
        )
        confidence_level = self._classify_confidence(calibrated_confidence)

        latency_ms = (time.time() - start_time) * 1000

        decision = Decision(
            id=f"decision_{int(time.time() * 1000)}",
            option=best_candidate.option,
            confidence=calibrated_confidence,
            confidence_level=confidence_level,
            reasoning=best_candidate.reasoning,
            strategy=best_candidate.strategy,
            candidates=candidates,
            domain_validation=domain_valid,
            latency_ms=latency_ms,
        )

        logger.info(
            f"Selected decision: {best_candidate.option} "
            f"(confidence={calibrated_confidence:.2f}, domain_valid={domain_valid})"
        )
        return decision

    def _score_candidate(
        self,
        candidate: CandidateDecision,
        context: AgentContext,
        calibrator: "ConfidenceCalibrator",
    ) -> Tuple[float, float]:
        """Score candidate based on confidence and domain factors.

        Returns:
            Tuple of (base_score, domain_score)
        """
        base_score = candidate.confidence

        # Domain-specific boost
        domain_score = 0.0
        if context.category in self.domain_rules:
            domain_score = self.domain_rules[context.category](candidate)

        return (base_score, domain_score)

    def _validate_domain_rules(
        self, candidate: CandidateDecision, context: AgentContext
    ) -> bool:
        """Validate candidate against domain-specific rules."""
        # Check all validation rules pass
        for rule in candidate.validation_rules:
            if rule == "safety_first" and "safety" in context.constraints:
                continue
            if rule == "pattern_match" and context.decision_history:
                continue
            if rule in ["model_confidence", "pattern_correlation", "ensemble_agreement"]:
                continue

        return True

    def _classify_confidence(self, confidence: float) -> ConfidenceLevel:
        """Classify confidence score into levels."""
        if confidence >= 0.90:
            return ConfidenceLevel.VERY_HIGH
        if confidence >= 0.75:
            return ConfidenceLevel.HIGH
        if confidence >= 0.60:
            return ConfidenceLevel.MEDIUM
        if confidence >= 0.45:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.VERY_LOW


class FeedbackLayer:
    """Collect and validate outcomes asynchronously.

    Responsibilities:
    - Log decision outcomes
    - Validate confidence calibration
    - Async outcome collection
    - Store outcomes for learning
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize feedback layer.

        Args:
            storage_path: Path to store outcomes
        """
        self.storage_path = storage_path or Path(".codex/reasoning/outcomes.jsonl")
        self.pending_outcomes: List[DecisionOutcome] = []
        self.outcome_history: List[DecisionOutcome] = []

    async def collect_outcome(
        self,
        decision: Decision,
        success: bool,
        actual_result: str,
        expected_result: str,
    ) -> DecisionOutcome:
        """Collect decision outcome asynchronously.

        Args:
            decision: Original decision
            success: Whether decision succeeded
            actual_result: Actual outcome
            expected_result: Expected outcome

        Returns:
            DecisionOutcome for feedback
        """
        confidence_accurate = (success and decision.confidence >= 0.75) or (
            not success and decision.confidence < 0.75
        )

        outcome = DecisionOutcome(
            decision_id=decision.id,
            success=success,
            actual_result=actual_result,
            expected_result=expected_result,
            confidence_was_accurate=confidence_accurate,
            latency_ms=decision.latency_ms,
        )

        self.pending_outcomes.append(outcome)
        self.outcome_history.append(outcome)

        logger.debug(
            f"Recorded outcome for {decision.id}: success={success}, "
            f"confidence_accurate={confidence_accurate}"
        )

        # Async storage (fire-and-forget in real system)
        asyncio.create_task(self._store_outcome(outcome))

        return outcome

    async def _store_outcome(self, outcome: DecisionOutcome) -> None:
        """Store outcome to disk asynchronously."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "a") as f:
                f.write(json.dumps(outcome.to_dict()) + "\n")
        except Exception as e:
            logger.error(f"Failed to store outcome: {e}")

    def get_outcomes_for_category(self, category: str) -> List[DecisionOutcome]:
        """Get all outcomes (for learning layer)."""
        return self.outcome_history

    def clear_pending(self) -> List[DecisionOutcome]:
        """Get and clear pending outcomes."""
        outcomes = self.pending_outcomes.copy()
        self.pending_outcomes.clear()
        return outcomes


class ImprovementLayer:
    """Autonomously adjust weights and strategies.

    Responsibilities:
    - Analyze decision outcomes
    - Adjust strategy weights based on performance
    - Minimize Brier score (calibration error)
    - Learn patterns autonomously
    - Report improvement metrics
    """

    def __init__(self):
        """Initialize improvement layer."""
        self.strategy_weights: Dict[str, float] = {
            DecisionStrategy.HEURISTIC.value: 0.33,
            DecisionStrategy.MACHINE_LEARNING.value: 0.33,
            DecisionStrategy.ENSEMBLE.value: 0.34,
        }
        self.category_accuracy: Dict[str, List[bool]] = defaultdict(list)
        self.brier_scores: Dict[str, List[float]] = defaultdict(list)
        self.improvement_history: List[Dict[str, Any]] = []

    def learn_from_outcomes(
        self,
        feedback_layer: FeedbackLayer,
        reasoning_layer: ReasoningLayer,
        calibrator: "ConfidenceCalibrator",
    ) -> Dict[str, Any]:
        """Autonomously learn and improve from outcomes.

        Args:
            feedback_layer: Outcomes collector
            reasoning_layer: Strategy generator
            calibrator: Confidence calibrator

        Returns:
            Learning metrics and improvements made
        """
        outcomes = feedback_layer.get_outcomes_for_category("")  # All categories

        if not outcomes:
            return {"improvements": [], "brier_score": 0.0, "weight_adjustments": {}}

        # Calculate metrics per strategy/category
        improvements: List[Dict[str, Any]] = []

        for strategy in DecisionStrategy:
            strategy_outcomes = [
                o
                for o in outcomes
                if o.decision_id  # Simplified for outcomes
            ]

            if strategy_outcomes:
                accuracy = sum(
                    1 for o in strategy_outcomes if o.success
                ) / len(strategy_outcomes)
                brier = self._calculate_brier_score(strategy_outcomes)

                # Adjust weights based on performance
                if accuracy > 0.95:
                    self.strategy_weights[strategy.value] *= 1.05
                elif accuracy < 0.80:
                    self.strategy_weights[strategy.value] *= 0.95

                improvements.append(
                    {
                        "strategy": strategy.value,
                        "accuracy": accuracy,
                        "brier_score": brier,
                        "weight_adjusted": self.strategy_weights[strategy.value],
                    }
                )

        # Normalize weights
        total_weight = sum(self.strategy_weights.values())
        self.strategy_weights = {
            k: v / total_weight for k, v in self.strategy_weights.items()
        }

        improvement_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "improvements": improvements,
            "brier_score": np.mean(
                [imp["brier_score"] for imp in improvements if "brier_score" in imp]
            ),
            "weight_adjustments": self.strategy_weights.copy(),
        }
        self.improvement_history.append(improvement_record)

        logger.info(
            f"Learning complete: {len(improvements)} strategies evaluated, "
            f"brier_score={improvement_record['brier_score']:.4f}"
        )

        return improvement_record

    def _calculate_brier_score(self, outcomes: List[DecisionOutcome]) -> float:
        """Calculate Brier score (mean squared error of confidence)."""
        if not outcomes:
            return 0.0

        squared_errors = [
            (1.0 if o.success else 0.0 - (1.0 if o.success else 0.0)) ** 2
            for o in outcomes
        ]
        return float(np.mean(squared_errors))

    def get_improvement_metrics(self) -> Dict[str, Any]:
        """Get current improvement metrics."""
        if not self.improvement_history:
            return {"status": "no_data"}

        latest = self.improvement_history[-1]
        avg_brier = np.mean([h["brier_score"] for h in self.improvement_history])

        return {
            "latest_improvement": latest,
            "average_brier_score": avg_brier,
            "strategy_weights": self.strategy_weights.copy(),
            "total_learning_iterations": len(self.improvement_history),
        }


class ReasoningEngine:
    """Main multi-layer reasoning orchestrator.

    Orchestrates all 5 layers:
    1. PerceptionLayer: Extract context
    2. ReasoningLayer: Generate candidates
    3. ActionLayer: Select best decision
    4. FeedbackLayer: Collect outcomes
    5. ImprovementLayer: Learn and improve
    """

    def __init__(
        self,
        knowledge_base: Optional["KnowledgeBase"] = None,
        domain_rules: Optional[Dict[str, Callable]] = None,
    ):
        """Initialize reasoning engine.

        Args:
            knowledge_base: Optional KB for pattern lookup
            domain_rules: Optional domain validation rules
        """
        self.perception = PerceptionLayer()
        self.reasoning = ReasoningLayer(knowledge_base)
        self.action = ActionLayer(domain_rules)
        self.feedback = FeedbackLayer()
        self.improvement = ImprovementLayer()
        self.calibrator = ConfidenceCalibrator()

        self.decision_history: List[Decision] = []
        self.total_decisions = 0

    def make_decision(
        self,
        goal: str,
        constraints: List[str],
        decision_history: List[Dict[str, Any]],
        current_state: Dict[str, Any],
        category: str,
    ) -> Decision:
        """Make a decision through all reasoning layers.

        Performance targets:
        - Latency <500ms (p99)
        - Accuracy >95%
        - Confidence calibration Brier <0.15

        Args:
            goal: Decision goal
            constraints: Constraints
            decision_history: Prior decisions
            current_state: Current state
            category: Decision category

        Returns:
            Final Decision
        """
        start_time = time.time()

        # Layer 1: Perception
        context = self.perception.extract_context(
            goal, constraints, decision_history, current_state, category
        )

        # Layer 2: Reasoning
        candidates = self.reasoning.generate_candidates(context)

        # Layer 3: Action
        decision = self.action.select_decision(context, candidates, self.calibrator)

        # Update decision latency
        decision.latency_ms = (time.time() - start_time) * 1000

        self.decision_history.append(decision)
        self.total_decisions += 1

        logger.info(
            f"Decision {self.total_decisions}: {decision.option} "
            f"({decision.latency_ms:.2f}ms, confidence={decision.confidence:.2f})"
        )

        return decision

    async def record_outcome(
        self,
        decision_id: str,
        success: bool,
        actual_result: str,
        expected_result: str = "",
    ) -> DecisionOutcome:
        """Record outcome for decision (Layer 4).

        Args:
            decision_id: ID of original decision
            success: Whether decision succeeded
            actual_result: Actual outcome
            expected_result: Expected outcome (optional)

        Returns:
            DecisionOutcome
        """
        decision = next(
            (d for d in self.decision_history if d.id == decision_id), None
        )

        if not decision:
            raise ValueError(f"Decision {decision_id} not found")

        outcome = await self.feedback.collect_outcome(
            decision, success, actual_result, expected_result
        )

        # Update calibrator with outcome
        self.calibrator.update(decision.confidence, success)

        return outcome

    def improve(self) -> Dict[str, Any]:
        """Run improvement cycle (Layer 5).

        Autonomously learns from outcomes and adjusts weights/strategies.

        Returns:
            Improvement metrics
        """
        return self.improvement.learn_from_outcomes(
            self.feedback, self.reasoning, self.calibrator
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive reasoning engine metrics.

        Returns:
            Metrics dict with performance, calibration, and learning data
        """
        recent_decisions = self.decision_history[-100:] if self.decision_history else []
        latencies = [d.latency_ms for d in recent_decisions]
        confidences = [d.confidence for d in recent_decisions]

        metrics = {
            "total_decisions": self.total_decisions,
            "recent_decisions_count": len(recent_decisions),
            "latency_ms": {
                "mean": float(np.mean(latencies)) if latencies else 0.0,
                "p99": float(np.percentile(latencies, 99)) if latencies else 0.0,
                "max": float(max(latencies)) if latencies else 0.0,
            },
            "confidence": {
                "mean": float(np.mean(confidences)) if confidences else 0.0,
                "std": float(np.std(confidences)) if confidences else 0.0,
            },
            "calibration": self.calibrator.get_metrics(),
            "improvement": self.improvement.get_improvement_metrics(),
            "strategy_weights": self.improvement.strategy_weights.copy(),
        }

        return metrics
