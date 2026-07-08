"""Tests for QEC k₁ tuning — Phase 10D coverage.

Covers AdaptiveScoringOptimizer k₁ lifecycle:
- Initial k₁ = 0.40
- Feedback-driven k₁ convergence toward ≤ 0.35
- Weight update mechanics, gradient computation
- Scoring function creation and boundary conditions
"""

from __future__ import annotations

import time

import pytest

from cognitive_brain.quantum.adaptive_scoring import (
    AdaptiveScoringEngine,
    AdaptiveScoringOptimizer,
    FeedbackRecord,
    ScoringWeights,
    create_scoring_function,
)

# ---------------------------------------------------------------------------
# ScoringWeights
# ---------------------------------------------------------------------------


class TestScoringWeights:
    def test_default_weights_sum(self):
        w = ScoringWeights()
        total = w.compliance_score_weight + w.risk_weight + w.cost_weight + w.impact_weight
        assert total == pytest.approx(1.0), "total is not valid"

    def test_normalize(self):
        w = ScoringWeights(
            compliance_score_weight=2.0,
            risk_weight=2.0,
            cost_weight=1.0,
            impact_weight=1.0,
        )
        n = w.normalize()
        total = n.compliance_score_weight + n.risk_weight + n.cost_weight + n.impact_weight
        assert total == pytest.approx(1.0), "total is not valid"

    def test_normalize_zero(self):
        w = ScoringWeights(
            compliance_score_weight=0,
            risk_weight=0,
            cost_weight=0,
            impact_weight=0,
        )
        n = w.normalize()
        # Should return self unchanged (all zeros)
        assert n.compliance_score_weight == 0, "compliance_score_weight is not valid"

    def test_to_dict(self):
        w = ScoringWeights()
        d = w.to_dict()
        assert "compliance_score_weight" in d, "Condition must be true"
        assert "risk_weight" in d, "Condition must be true"


# ---------------------------------------------------------------------------
# AdaptiveScoringOptimizer — k₁ lifecycle
# ---------------------------------------------------------------------------


class TestAdaptiveScoringOptimizer:
    @pytest.fixture()
    def optimizer(self):
        return AdaptiveScoringOptimizer(learning_rate=0.12, momentum=0.9)

    def test_initial_k1(self, optimizer):
        """k₁ starts at 0.40."""
        assert optimizer.get_current_k1() == pytest.approx(0.40), "Condition must be true"

    def test_k1_history_starts_populated(self, optimizer):
        assert len(optimizer.k1_history) == 1, "Collection must not be empty"
        assert optimizer.k1_history[0] == 0.40, "Condition must be true"

    def test_compute_score_default_features(self, optimizer):
        score = optimizer.compute_score({})
        assert 0.0 <= score <= 1.0, "0 is not valid"

    def test_compute_score_high_compliance(self, optimizer):
        features = {
            "compliance_score": 1.0,
            "risk_score": 0.0,
            "cost_score": 0.0,
            "impact_score": 1.0,
        }
        score = optimizer.compute_score(features)
        assert score > 0.5, "score must be greater than zero"

    def test_compute_score_clamped(self, optimizer):
        # Extreme features should still be clamped to [0, 1]
        features = {
            "compliance_score": 10.0,
            "risk_score": -5.0,
            "cost_score": -5.0,
            "impact_score": 10.0,
        }
        score = optimizer.compute_score(features)
        assert 0.0 <= score <= 1.0, "0 is not valid"

    def test_add_feedback(self, optimizer):
        fb = FeedbackRecord(
            audit_id="A1",
            predicted_decision="approve",
            actual_decision="approve",
            is_correct=True,
            audit_features={"compliance_score": 0.8},
            timestamp=time.time(),
        )
        optimizer.add_feedback(fb)
        assert len(optimizer.feedback_history) == 1, "Collection must not be empty"

    def test_update_weights_needs_minimum(self, optimizer):
        """Weight update requires ≥ 5 feedback records."""
        for i in range(3):
            optimizer.add_feedback(
                FeedbackRecord(
                    audit_id=f"A{i}",
                    predicted_decision="approve",
                    actual_decision="approve",
                    is_correct=True,
                    audit_features={"compliance_score": 0.8},
                    timestamp=time.time(),
                )
            )
        changes = optimizer.update_weights()
        assert changes == {}, "changes is not valid"

    def test_k1_converges_with_correct_feedback(self, optimizer):
        """With high accuracy feedback, k₁ should decrease toward target."""
        for i in range(10):
            optimizer.add_feedback(
                FeedbackRecord(
                    audit_id=f"A{i}",
                    predicted_decision="approve",
                    actual_decision="approve",
                    is_correct=True,
                    audit_features={
                        "compliance_score": 0.9,
                        "risk_score": 0.1,
                        "cost_score": 0.2,
                        "impact_score": 0.8,
                    },
                    timestamp=time.time(),
                )
            )
        optimizer.update_weights()
        # k₁ should have been updated
        assert len(optimizer.k1_history) > 1, "Collection must not be empty"
        # With 100% accuracy: k₁ = 0.40 * (1 - (1.0 - 0.5) * 0.2) = 0.40 * 0.9 = 0.36
        latest_k1 = optimizer.get_current_k1()
        assert latest_k1 < 0.40, "latest_k1 is not valid"

    def test_k1_with_mixed_feedback(self, optimizer):
        """With mixed accuracy, k₁ stays closer to 0.40."""
        for i in range(10):
            optimizer.add_feedback(
                FeedbackRecord(
                    audit_id=f"A{i}",
                    predicted_decision="approve",
                    actual_decision="reject" if i % 2 == 0 else "approve",
                    is_correct=i % 2 != 0,
                    audit_features={
                        "compliance_score": 0.5,
                        "risk_score": 0.5,
                        "cost_score": 0.5,
                        "impact_score": 0.5,
                    },
                    timestamp=time.time(),
                )
            )
        optimizer.update_weights()
        k1 = optimizer.get_current_k1()
        # 50% accuracy: k₁ = 0.40 * (1 - (0.5 - 0.5) * 0.2) = 0.40
        assert k1 == pytest.approx(0.40), "k1 is not valid"

    def test_get_accuracy_empty(self, optimizer):
        assert optimizer.get_accuracy() == 0.0, "Condition must be true"

    def test_get_accuracy_computed(self, optimizer):
        for i in range(4):
            optimizer.add_feedback(
                FeedbackRecord(
                    audit_id=f"A{i}",
                    predicted_decision="approve",
                    actual_decision="approve",
                    is_correct=i < 3,  # 3/4 correct
                    audit_features={},
                    timestamp=time.time(),
                )
            )
        assert optimizer.get_accuracy() == pytest.approx(0.75), "Condition must be true"

    def test_reset_weights(self, optimizer):
        optimizer.k1_history.append(0.35)
        optimizer.reset_weights()
        assert optimizer.get_current_k1() == 0.40, "Condition must be true"
        assert len(optimizer.k1_history) == 1, "Collection must not be empty"

    def test_backward_compat_alias(self):
        assert AdaptiveScoringEngine is AdaptiveScoringOptimizer, "AdaptiveScoringEngine is not valid"


# ---------------------------------------------------------------------------
# create_scoring_function
# ---------------------------------------------------------------------------


class TestCreateScoringFunction:
    def test_returns_callable(self):
        opt = AdaptiveScoringOptimizer()
        fn = create_scoring_function(opt)
        assert callable(fn), "Condition must be true"

    def test_scoring_fn_delegates(self):
        opt = AdaptiveScoringOptimizer()
        fn = create_scoring_function(opt)
        features = {"compliance_score": 0.7, "risk_score": 0.3}
        assert fn(features) == opt.compute_score(features), "Condition must be true"


# ---------------------------------------------------------------------------
# Gradient computation
# ---------------------------------------------------------------------------


class TestGradients:
    def test_gradients_all_correct(self):
        opt = AdaptiveScoringOptimizer()
        feedbacks = [
            FeedbackRecord(
                audit_id=f"A{i}",
                predicted_decision="approve",
                actual_decision="approve",
                is_correct=True,
                audit_features={"compliance_score": 0.8},
                timestamp=time.time(),
            )
            for i in range(5)
        ]
        grads = opt._compute_gradients(feedbacks)
        # All correct → all gradients should be zero
        assert all(v == 0.0 for v in grads.values()), "Value must be initialized"

    def test_gradients_with_errors(self):
        opt = AdaptiveScoringOptimizer()
        feedbacks = [
            FeedbackRecord(
                audit_id="A1",
                predicted_decision="approve",
                actual_decision="reject",
                is_correct=False,
                audit_features={
                    "compliance_score": 0.8,
                    "risk_score": 0.2,
                    "cost_score": 0.3,
                    "impact_score": 0.7,
                },
                timestamp=time.time(),
            ),
        ]
        grads = opt._compute_gradients(feedbacks)
        # Should have non-zero gradients
        assert any(v != 0.0 for v in grads.values()), "Value must be initialized"
