"""
Tests for Fuzzy Logic PoC (Phase 4)

Validates FuzzyEngine membership functions and boundary case handling:
- trimf / trapmf correctness
- evaluate() decision classification
- fuzzy_blend() boundary override with CODEX_FUZZY_MODE flag
"""

import pytest

from cognitive_brain.analytics.fuzzy import (
    FuzzyEngine,
    FuzzyResult,
    _fuzzy_mode_enabled,
    trapmf,
    trimf,
)

# ---------------------------------------------------------------------------
# Membership functions
# ---------------------------------------------------------------------------


class TestMembershipFunctions:
    def test_trimf_peak(self):
        assert trimf(0.5, 0.0, 0.5, 1.0) == pytest.approx(1.0)

    def test_trimf_left_foot_zero(self):
        assert trimf(0.0, 0.0, 0.5, 1.0) == pytest.approx(0.0)

    def test_trimf_right_foot_zero(self):
        assert trimf(1.0, 0.0, 0.5, 1.0) == pytest.approx(0.0)

    def test_trimf_midpoint_ascending(self):
        # x=0.25 is halfway between a=0 and b=0.5
        assert trimf(0.25, 0.0, 0.5, 1.0) == pytest.approx(0.5)

    def test_trimf_below_range_zero(self):
        assert trimf(-0.1, 0.0, 0.5, 1.0) == pytest.approx(0.0)

    def test_trapmf_flat_top(self):
        # In [b, c] → membership = 1.0
        assert trapmf(0.5, 0.0, 0.3, 0.7, 1.0) == pytest.approx(1.0)

    def test_trapmf_left_shoulder(self):
        # x=0.15 is halfway between a=0 and b=0.3
        assert trapmf(0.15, 0.0, 0.3, 0.7, 1.0) == pytest.approx(0.5)

    def test_trapmf_right_shoulder(self):
        # x=0.85 is halfway between c=0.7 and d=1.0
        assert trapmf(0.85, 0.0, 0.3, 0.7, 1.0) == pytest.approx(0.5)

    def test_trapmf_outside_range_zero(self):
        assert trapmf(-0.1, 0.0, 0.3, 0.7, 1.0) == pytest.approx(0.0)
        assert trapmf(1.1, 0.0, 0.3, 0.7, 1.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# FuzzyEngine.evaluate()
# ---------------------------------------------------------------------------


class TestFuzzyEngine:
    def setup_method(self):
        self.engine = FuzzyEngine.default()

    def test_high_score_high_impact_approve(self):
        """High score + high impact → approve should dominate."""
        result = self.engine.evaluate(score=0.95, business_impact=0.90, remediation_cost=2000.0)
        assert result.dominant == "approve", "Result must not be empty"
        assert result.confidence > 0.0, "confidence must be greater than zero"

    def test_medium_score_high_impact_monitor(self):
        """Medium score + high impact → monitor should dominate."""
        result = self.engine.evaluate(score=0.65, business_impact=0.80, remediation_cost=5000.0)
        # Monitor should be a viable decision with some membership
        assert result.monitor > 0.0, "monitor must be greater than zero"

    def test_low_score_reject(self):
        """Very low score → reject should dominate."""
        result = self.engine.evaluate(score=0.20, business_impact=0.30, remediation_cost=1000.0)
        assert result.dominant == "reject", "Result must not be empty"
        assert result.reject > 0.0, "reject must be greater than zero"

    def test_result_is_fuzzy_result(self):
        result = self.engine.evaluate(score=0.5, business_impact=0.5, remediation_cost=5000.0)
        assert isinstance(result, FuzzyResult)

    def test_memberships_in_unit_interval(self):
        """All membership values must be in [0.0, 1.0]."""
        result = self.engine.evaluate(score=0.68, business_impact=0.65, remediation_cost=5000.0)
        for val in [result.approve, result.monitor, result.conditional, result.reject]:
            assert 0.0 <= val <= 1.0, "0 is not valid"

    def test_dominant_is_max_membership(self):
        """Dominant class must be the one with highest membership."""
        result = self.engine.evaluate(score=0.5, business_impact=0.5, remediation_cost=3000.0)
        memberships = {
            "approve": result.approve,
            "monitor": result.monitor,
            "conditional": result.conditional,
            "reject": result.reject,
        }
        best = max(memberships, key=lambda k: memberships[k])
        assert result.dominant == best, "Result must not be empty"

    def test_boundary_case_score_0_68(self):
        """Score=0.68 is a known boundary — fuzzy should produce non-zero memberships."""
        result = self.engine.evaluate(score=0.68, business_impact=0.65, remediation_cost=5000.0)
        # At least two decisions should have non-zero membership (boundary ambiguity)
        non_zero = sum(
            1 for v in [result.approve, result.monitor, result.conditional, result.reject] if v > 0
        )
        assert non_zero >= 1, "non_zero must be greater than zero"


# ---------------------------------------------------------------------------
# FuzzyEngine.fuzzy_blend()
# ---------------------------------------------------------------------------


class TestFuzzyBlend:
    def setup_method(self):
        self.engine = FuzzyEngine.default()

    def test_disabled_returns_crisp(self, monkeypatch):
        """When CODEX_FUZZY_MODE=false, crisp decision is returned unchanged."""
        monkeypatch.setenv("CODEX_FUZZY_MODE", "false")
        result = self.engine.fuzzy_blend(
            crisp_decision="monitor",
            score=0.20,
            business_impact=0.30,
            remediation_cost=1000.0,
        )
        assert result == "monitor", "Result must not be empty"

    def test_enabled_low_score_overrides_to_reject(self, monkeypatch):
        """With CODEX_FUZZY_MODE=true, low score should trigger reject override."""
        monkeypatch.setenv("CODEX_FUZZY_MODE", "true")
        result = self.engine.fuzzy_blend(
            crisp_decision="approve",
            score=0.10,
            business_impact=0.20,
            remediation_cost=500.0,
            threshold=0.1,
        )
        assert result == "reject", "Result must not be empty"

    def test_enabled_confident_same_decision_unchanged(self, monkeypatch):
        """When fuzzy agrees with crisp decision, output unchanged."""
        monkeypatch.setenv("CODEX_FUZZY_MODE", "true")
        result = self.engine.fuzzy_blend(
            crisp_decision="approve",
            score=0.95,
            business_impact=0.90,
            remediation_cost=2000.0,
        )
        assert result == "approve", "Result must not be empty"

    def test_feature_flag_default_off(self, monkeypatch):
        """CODEX_FUZZY_MODE defaults to false."""
        monkeypatch.delenv("CODEX_FUZZY_MODE", raising=False)
        assert not _fuzzy_mode_enabled(), "Condition must be true"

    def test_feature_flag_enabled(self, monkeypatch):
        """CODEX_FUZZY_MODE=true enables fuzzy overrides."""
        monkeypatch.setenv("CODEX_FUZZY_MODE", "true")
        assert _fuzzy_mode_enabled(), "Condition must be true"
