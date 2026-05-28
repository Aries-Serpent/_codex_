"""
Adaptive Scoring Optimizer for Superposition Engine

This module implements machine-learning-inspired adaptive scoring to optimize
decision quality in ambiguous scenarios. Learns from feedback to improve weights.

Rayleigh-Inspired Design:
- k₁ optimization through weight tuning
- Resolution enhancement via feedback learning
- Process window control through learning rate

PDA Loop + AfterMath Pattern:
- PLAN: Initialize weights, define update strategy
- DO: Process feedback, update weights
- ASSESS: Measure accuracy improvement
- AfterMath: Track k₁ reduction, coherence trends
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ScoringWeights:
    """Weights for compliance scoring factors (Phase 8.0 optimized)"""

    compliance_score_weight: float = 0.38  # Reduced from 0.40 (-5%)
    risk_weight: float = 0.32  # Increased from 0.30 (+6.7%)
    cost_weight: float = 0.15  # Unchanged
    impact_weight: float = 0.15  # Unchanged

    def normalize(self) -> "ScoringWeights":
        """Normalize weights to sum to 1.0"""
        total = (
            self.compliance_score_weight + self.risk_weight + self.cost_weight + self.impact_weight
        )
        if total == 0:
            return self
        return ScoringWeights(
            compliance_score_weight=self.compliance_score_weight / total,
            risk_weight=self.risk_weight / total,
            cost_weight=self.cost_weight / total,
            impact_weight=self.impact_weight / total,
        )

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary"""
        return {
            "compliance_score_weight": self.compliance_score_weight,
            "risk_weight": self.risk_weight,
            "cost_weight": self.cost_weight,
            "impact_weight": self.impact_weight,
        }


@dataclass
class FeedbackRecord:
    """Record of decision feedback for learning"""

    audit_id: str
    predicted_decision: str
    actual_decision: str
    is_correct: bool
    audit_features: dict[str, float]  # Normalized features
    timestamp: float


class AdaptiveScoringOptimizer:
    """
    Adaptive optimizer for superposition scoring functions.

    Uses feedback-driven learning to tune scoring weights for better accuracy
    in ambiguous compliance scenarios.

    Learning Algorithm:
    - Exponential moving average of gradient updates
    - Momentum-based weight adjustments
    - Gradient descent with configurable learning rate

    Rayleigh Metrics:
    - Tracks k₁ (process factor) improvement
    - Monitors resolution enhancement
    - Measures DOF (process window)
    """

    def __init__(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: list[FeedbackRecord] = []
        self.velocity: dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: list[float] = [0.40]  # Track k₁ reduction

    def compute_score(self, features: dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def add_feedback(self, feedback: FeedbackRecord) -> None:
        """
        Add feedback record for learning.

        Args:
            feedback: FeedbackRecord with decision outcome
        """
        self.feedback_history.append(feedback)

    def update_weights(self) -> dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"] + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]),
            cost_weight=max(0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]),
            impact_weight=max(0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights}

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def _compute_gradients(self, feedback_batch: list[FeedbackRecord]) -> dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (1.0 - features.get("risk_score", 0.5))
                gradients["cost_weight"] += factor * (1.0 - features.get("cost_score", 0.5))
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def _needs_lower_score(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"reject", "REJECT"}
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject and not actual_is_reject

    def get_current_k1(self) -> float:
        """Get current k₁ estimate"""
        return self.k1_history[-1] if self.k1_history else 0.40

    def tune_k1_from_pda_history(
        self,
        pda_path: str | Path = ".codex/aftermath/pda_iterations.jsonl",
        *,
        prior_alpha: float = 2.0,
        prior_beta: float = 2.0,
        max_records: int = 500,
    ) -> float:
        """
        Tune k₁ using Bayesian success-rate estimation from PDA session history.

        The posterior mean success probability is mapped to the k₁ process factor.
        Higher observed success lowers k₁.
        """
        path = Path(pda_path)
        if not path.exists():
            return self.get_current_k1()

        records = path.read_text(encoding="utf-8").splitlines()[-max_records:]
        outcomes: list[int] = []
        for line in records:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            success = self._extract_success_signal(payload)
            if success is None:
                continue
            outcomes.append(1 if success else 0)

        if not outcomes:
            return self.get_current_k1()

        alpha = prior_alpha + sum(outcomes)
        beta = prior_beta + (len(outcomes) - sum(outcomes))
        posterior_success = alpha / (alpha + beta)

        # Map posterior success to bounded k₁ target space.
        tuned_k1 = max(0.20, min(0.45, 0.45 - (0.20 * posterior_success)))
        self.k1_history.append(tuned_k1)
        return tuned_k1

    def _extract_success_signal(self, payload: dict[str, Any]) -> bool | None:
        """Extract a binary success signal from a PDA JSONL row."""
        green = payload.get("ci_checks_green")
        red = payload.get("ci_checks_red")
        if (
            isinstance(green, (int, float))
            and not isinstance(green, bool)
            and isinstance(red, (int, float))
            and not isinstance(red, bool)
        ):
            return green > red

        status = str(payload.get("status", "")).strip().lower()
        if status in {"complete", "completed", "resolved", "implemented", "success", "ok"}:
            return True
        if status in {"failed", "failure", "error", "aborted", "blocked"}:
            return False
        return None

    def get_accuracy(self) -> float:
        """Get current accuracy from feedback"""
        if not self.feedback_history:
            return 0.0
        recent = self.feedback_history[-50:]
        return sum(1 for f in recent if f.is_correct) / len(recent)

    def reset_weights(self) -> None:
        """Reset weights to initial values"""
        self.weights = ScoringWeights().normalize()
        self.velocity = {k: 0.0 for k in self.velocity}
        self.k1_history = [0.40]


def create_scoring_function(
    optimizer: AdaptiveScoringOptimizer,
) -> Callable[[dict[str, float]], float]:
    """
    Create a scoring function using the optimizer's current weights.

    Args:
        optimizer: AdaptiveScoringOptimizer instance

    Returns:
        Scoring function that takes feature dict and returns score
    """

    def scoring_fn(features: dict[str, float]) -> float:
        return optimizer.compute_score(features)

    return scoring_fn


# Backward-compatible alias for imports
AdaptiveScoringEngine = AdaptiveScoringOptimizer
