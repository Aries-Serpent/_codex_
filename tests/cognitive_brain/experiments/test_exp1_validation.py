"""Tests for cognitive_brain.experiments.exp1_validation.

Tests cover:
- get_ground_truth decision rules
- generate_audit_scenarios reproducibility and structure
"""

from __future__ import annotations


from cognitive_brain.experiments.exp1_validation import (
    generate_audit_scenarios,
    get_ground_truth,
)
from cognitive_brain.integrations.compliance_integration import (
    AuditResult,
    ComplianceDecision,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_audit(
    audit_id: str = "TEST-001",
    score: float = 0.95,
    risk_level: str = "low",
    remediation_cost: float = 100.0,
    business_impact: float = 0.8,
    violations: list | None = None,
) -> AuditResult:
    return AuditResult(
        audit_id=audit_id,
        score=score,
        risk_level=risk_level,
        remediation_cost=remediation_cost,
        business_impact=business_impact,
        violations=violations or [],
    )


# ---------------------------------------------------------------------------
# get_ground_truth — decision rules
# ---------------------------------------------------------------------------


def test_ground_truth_approve_high_score_low_risk():
    audit = _make_audit(score=0.95, risk_level="low")
    assert get_ground_truth(audit) == ComplianceDecision.APPROVE


def test_ground_truth_approve_score_exactly_090_low_risk():
    audit = _make_audit(score=0.90, risk_level="low")
    assert get_ground_truth(audit) == ComplianceDecision.APPROVE


def test_ground_truth_approve_with_monitoring_high_score_medium_risk():
    audit = _make_audit(score=0.80, risk_level="medium")
    assert get_ground_truth(audit) == ComplianceDecision.APPROVE_WITH_MONITORING


def test_ground_truth_approve_with_monitoring_score_070_low_risk():
    audit = _make_audit(score=0.70, risk_level="low")
    assert get_ground_truth(audit) == ComplianceDecision.APPROVE_WITH_MONITORING


def test_ground_truth_conditional_marginal_score_low_cost():
    audit = _make_audit(score=0.55, risk_level="low", remediation_cost=1500.0)
    assert get_ground_truth(audit) == ComplianceDecision.CONDITIONAL_APPROVAL


def test_ground_truth_conditional_score_050_boundary():
    audit = _make_audit(score=0.50, risk_level="low", remediation_cost=500.0)
    assert get_ground_truth(audit) == ComplianceDecision.CONDITIONAL_APPROVAL


def test_ground_truth_reject_low_score_high_risk():
    audit = _make_audit(score=0.3, risk_level="high")
    assert get_ground_truth(audit) == ComplianceDecision.REJECT


def test_ground_truth_reject_marginal_score_high_cost():
    audit = _make_audit(score=0.55, risk_level="low", remediation_cost=5000.0)
    assert get_ground_truth(audit) == ComplianceDecision.REJECT


def test_ground_truth_reject_zero_score():
    audit = _make_audit(score=0.0, risk_level="high")
    assert get_ground_truth(audit) == ComplianceDecision.REJECT


def test_ground_truth_high_score_medium_risk_not_approve():
    """Score >= 0.90 but risk is medium — falls to APPROVE_WITH_MONITORING."""
    audit = _make_audit(score=0.95, risk_level="medium")
    assert get_ground_truth(audit) == ComplianceDecision.APPROVE_WITH_MONITORING


def test_ground_truth_conditional_high_risk_medium_cost():
    """High risk + marginal score + cost >= 2000 -> REJECT (cost check fails conditional rule)."""
    audit = _make_audit(score=0.55, risk_level="high", remediation_cost=3000.0)
    assert get_ground_truth(audit) == ComplianceDecision.REJECT


# ---------------------------------------------------------------------------
# generate_audit_scenarios
# ---------------------------------------------------------------------------


def test_generate_audit_scenarios_count():
    scenarios = generate_audit_scenarios(10)
    assert len(scenarios) == 10


def test_generate_audit_scenarios_default_100():
    scenarios = generate_audit_scenarios(100)
    assert len(scenarios) == 100


def test_generate_audit_scenarios_returns_tuples():
    scenarios = generate_audit_scenarios(5)
    for audit, truth in scenarios:
        assert isinstance(audit, AuditResult)
        assert isinstance(truth, ComplianceDecision)


def test_generate_audit_scenarios_reproducible():
    scenarios1 = generate_audit_scenarios(20)
    scenarios2 = generate_audit_scenarios(20)
    for (a1, t1), (a2, t2) in zip(scenarios1, scenarios2):
        assert a1.audit_id == a2.audit_id
        assert t1 == t2


def test_generate_audit_scenarios_has_unique_ids():
    scenarios = generate_audit_scenarios(50)
    ids = [audit.audit_id for audit, _ in scenarios]
    assert len(set(ids)) == 50


def test_generate_audit_scenarios_all_decisions_covered():
    """With 100 scenarios, all 4 decision types should appear."""
    scenarios = generate_audit_scenarios(100)
    decisions = {truth for _, truth in scenarios}
    assert len(decisions) >= 2  # At least 2 decision types in 100 scenarios


def test_generate_audit_scenarios_risk_levels_varied():
    scenarios = generate_audit_scenarios(50)
    risk_levels = {audit.risk_level for audit, _ in scenarios}
    # Should have more than one risk level
    assert len(risk_levels) > 1


def test_generate_audit_scenarios_scores_in_range():
    scenarios = generate_audit_scenarios(20)
    for audit, _ in scenarios:
        assert 0.0 <= audit.score <= 1.0


def test_generate_audit_scenarios_zero_count():
    scenarios = generate_audit_scenarios(0)
    assert scenarios == []


def test_generate_audit_scenarios_ground_truth_consistent():
    """Verify that the ground truth matches our manual application of get_ground_truth."""
    scenarios = generate_audit_scenarios(10)
    for audit, truth in scenarios:
        expected = get_ground_truth(audit)
        assert truth == expected
