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

from dataclasses import dataclass
from typing import Dict, List, Callable, Any
import math


@dataclass
class ScoringWeights:
    """Weights for compliance scoring factors (Phase 8.0 optimized)"""
    compliance_score_weight: float = 0.38  # Reduced from 0.40 (-5%)
    risk_weight: float = 0.32              # Increased from 0.30 (+6.7%)
    cost_weight: float = 0.15              # Unchanged
    impact_weight: float = 0.15            # Unchanged
    
    def normalize(self) -> 'ScoringWeights':
        """Normalize weights to sum to 1.0"""
        total = (self.compliance_score_weight + self.risk_weight + 
                 self.cost_weight + self.impact_weight)
        if total == 0:
            return self
        return ScoringWeights(
            compliance_score_weight=self.compliance_score_weight / total,
            risk_weight=self.risk_weight / total,
            cost_weight=self.cost_weight / total,
            impact_weight=self.impact_weight / total
        )
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            'compliance_score_weight': self.compliance_score_weight,
            'risk_weight': self.risk_weight,
            'cost_weight': self.cost_weight,
            'impact_weight': self.impact_weight
        }


@dataclass
class FeedbackRecord:
    """Record of decision feedback for learning"""
    audit_id: str
    predicted_decision: str
    actual_decision: str
    is_correct: bool
    audit_features: Dict[str, float]  # Normalized features
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
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            'compliance_score_weight': 0.0,
            'risk_weight': 0.0,
            'cost_weight': 0.0,
            'impact_weight': 0.0
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction
    
    def compute_score(self, features: Dict[str, float]) -> float:
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
            self.weights.compliance_score_weight * features.get('compliance_score', 0.5) +
            self.weights.risk_weight * (1.0 - features.get('risk_score', 0.5)) +  # Invert risk
            self.weights.cost_weight * (1.0 - features.get('cost_score', 0.5)) +  # Invert cost
            self.weights.impact_weight * features.get('impact_score', 0.5)
        )
        return max(0.0, min(1.0, score))
    
    def add_feedback(self, feedback: FeedbackRecord) -> None:
        """
        Add feedback record for learning.
        
        Args:
            feedback: FeedbackRecord with decision outcome
        """
        self.feedback_history.append(feedback)
    
    def update_weights(self) -> Dict[str, float]:
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
            self.velocity[key] = (
                self.momentum * self.velocity[key] +
                self.learning_rate * gradients.get(key, 0.0)
            )
        
        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(0.0, old_weights['compliance_score_weight'] + self.velocity['compliance_score_weight']),
            risk_weight=max(0.0, old_weights['risk_weight'] + self.velocity['risk_weight']),
            cost_weight=max(0.0, old_weights['cost_weight'] + self.velocity['cost_weight']),
            impact_weight=max(0.0, old_weights['impact_weight'] + self.velocity['impact_weight'])
        )
        self.weights = new_weights.normalize()
        
        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key]
            for key in old_weights
        }
        
        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)
        
        return changes
    
    def _compute_gradients(self, feedback_batch: List[FeedbackRecord]) -> Dict[str, float]:
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
            'compliance_score_weight': 0.0,
            'risk_weight': 0.0,
            'cost_weight': 0.0,
            'impact_weight': 0.0
        }
        
        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features
                
                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1
                
                gradients['compliance_score_weight'] += factor * features.get('compliance_score', 0.5)
                gradients['risk_weight'] += factor * (1.0 - features.get('risk_score', 0.5))
                gradients['cost_weight'] += factor * (1.0 - features.get('cost_score', 0.5))
                gradients['impact_weight'] += factor * features.get('impact_score', 0.5)
        
        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count
        
        return gradients
    
    def _needs_lower_score(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {'reject', 'REJECT'}
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject and not actual_is_reject
    
    def get_current_k1(self) -> float:
        """Get current k₁ estimate"""
        return self.k1_history[-1] if self.k1_history else 0.40
    
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


def create_scoring_function(optimizer: AdaptiveScoringOptimizer) -> Callable[[Dict[str, float]], float]:
    """
    Create a scoring function using the optimizer's current weights.
    
    Args:
        optimizer: AdaptiveScoringOptimizer instance
    
    Returns:
        Scoring function that takes feature dict and returns score
    """
    def scoring_fn(features: Dict[str, float]) -> float:
        return optimizer.compute_score(features)
    return scoring_fn


class AdaptiveScoringEngine:
    """
    Simplified adaptive scoring engine for scenario-based scoring.

    Provides a lightweight interface for tests that expect tunable weights,
    trainable updates, and robust handling of edge-case inputs.
    """

    def __init__(
        self,
        compliance_score_weight: float = 0.38,
        risk_weight: float = 0.32,
        impact_weight: float = 0.15,
        mitigation_weight: float = 0.15,
        learning_rate: float = 0.12,
    ) -> None:
        self.learning_rate = learning_rate
        self.compliance_score_weight = compliance_score_weight
        self.risk_weight = risk_weight
        self.impact_weight = impact_weight
        self.mitigation_weight = mitigation_weight
        self._validate_and_normalize()

    def _validate_and_normalize(self) -> None:
        weights = [
            self.compliance_score_weight,
            self.risk_weight,
            self.impact_weight,
            self.mitigation_weight,
        ]
        if any(w < 0 for w in weights):
            raise ValueError("Weights must be non-negative")
        total = sum(weights)
        if total == 0:
            raise ValueError("Weights must sum to 1.0")
        if total > 1.0 + 1e-9:
            raise ValueError("Weights must sum to 1.0")
        if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-9):
            self.compliance_score_weight /= total
            self.risk_weight /= total
            self.impact_weight /= total
            self.mitigation_weight /= total

    def _safe_float(self, value: Any, default: float) -> float:
        try:
            val = float(value)
        except (TypeError, ValueError):
            return default
        if not math.isfinite(val):
            return default
        return val

    def _risk_to_score(self, risk: Any) -> float:
        if isinstance(risk, str):
            risk_key = risk.lower()
            return {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 0.95}.get(
                risk_key, 0.5
            )
        return self._safe_float(risk, 0.5)

    def _extract_features(self, scenario: Any) -> Dict[str, float]:
        audit = None
        complexity = None
        if isinstance(scenario, (tuple, list)) and scenario:
            audit = scenario[0]
            if len(scenario) > 2:
                complexity = scenario[2]
        else:
            audit = scenario

        compliance_score = self._safe_float(
            getattr(audit, "compliance_score", getattr(audit, "score", 0.5)), 0.5
        )
        risk_level = getattr(audit, "risk_level", 0.5)
        risk_score = self._risk_to_score(risk_level)
        impact_score = self._safe_float(
            getattr(audit, "business_impact", getattr(audit, "impact_score", 0.5)), 0.5
        )
        remediation_cost = self._safe_float(getattr(audit, "remediation_cost", 5000.0), 5000.0)
        mitigation_score = self._safe_float(
            getattr(audit, "mitigation_effectiveness", 1.0 - min(remediation_cost / 10000.0, 1.0)),
            0.5,
        )
        ambiguity_score = self._safe_float(
            getattr(complexity, "ambiguity_score", getattr(audit, "ambiguity_score", 0.5)), 0.5
        )
        return {
            "compliance_score": max(0.0, min(1.0, compliance_score)),
            "risk_score": max(0.0, min(1.0, risk_score)),
            "impact_score": max(0.0, min(1.0, impact_score)),
            "mitigation_score": max(0.0, min(1.0, mitigation_score)),
            "ambiguity_score": max(0.0, min(1.0, ambiguity_score)),
        }

    def compute_score(self, scenario: Any) -> float:
        features = self._extract_features(scenario)
        base = (
            self.compliance_score_weight * features["compliance_score"]
            + self.risk_weight * (1.0 - features["risk_score"])
            + self.impact_weight * features["impact_score"]
            + self.mitigation_weight * features["mitigation_score"]
        )
        ambiguity_penalty = 1.0 - 0.2 * features["ambiguity_score"]
        score = max(0.0, min(1.0, base * ambiguity_penalty))
        return score * 100.0

    def train(self, scenarios: List[Any], epochs: int = 1) -> None:
        if not scenarios:
            raise ValueError("Cannot train on empty scenarios")
        if self.learning_rate == 0:
            return

        for _ in range(max(1, epochs)):
            aggregates = {
                "compliance": 0.0,
                "risk": 0.0,
                "impact": 0.0,
                "mitigation": 0.0,
            }
            for scenario in scenarios:
                feats = self._extract_features(scenario)
                aggregates["compliance"] += feats["compliance_score"]
                aggregates["risk"] += 1.0 - feats["risk_score"]
                aggregates["impact"] += feats["impact_score"]
                aggregates["mitigation"] += feats["mitigation_score"]
            count = len(scenarios)
            if count == 0:
                return
            target = {k: v / count for k, v in aggregates.items()}

            self.compliance_score_weight += self.learning_rate * (
                target["compliance"] - self.compliance_score_weight
            )
            self.risk_weight += self.learning_rate * (target["risk"] - self.risk_weight)
            self.impact_weight += self.learning_rate * (
                target["impact"] - self.impact_weight
            )
            self.mitigation_weight += self.learning_rate * (
                target["mitigation"] - self.mitigation_weight
            )
            self._validate_and_normalize()
