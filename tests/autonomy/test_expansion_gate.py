"""
Tests for Phase 6 — Safe Autonomy Expansion Gate
(src/codex/autonomy/expansion_gate.py)
"""

from __future__ import annotations

import pytest

from codex.autonomy.expansion_gate import (
    _AUDIT_COVERAGE_THRESHOLD,
    _GI_THRESHOLD,
    _LP_THRESHOLD,
    BASELINE_AP,
    BASELINE_GI,
    BASELINE_LP,
    BASELINE_Q,
    TARGET_GI,
    TARGET_LP,
    TARGET_Q,
    ExpansionGate,
    GateResult,
)


def _gate(gi=0.85, lp=0.88, deny=0.12, audit=0.97) -> ExpansionGate:
    return ExpansionGate(
        governance_integrity=gi,
        least_privilege=lp,
        deny_rate_guarded=deny,
        audit_coverage=audit,
    )


class TestExpansionGateBaseline:
    def test_baseline_constants_match_blueprint(self):
        assert BASELINE_AP == pytest.approx(0.877)
        assert BASELINE_GI == pytest.approx(0.5405)
        assert BASELINE_LP == pytest.approx(0.57)
        assert BASELINE_Q == pytest.approx(BASELINE_AP * BASELINE_GI * BASELINE_LP, abs=1e-3)

    def test_target_quality_matches_blueprint(self):
        expected = BASELINE_AP * TARGET_GI * TARGET_LP
        assert TARGET_Q == pytest.approx(expected, abs=1e-3)
        assert TARGET_Q > 0.6  # blueprint says ≈ 0.656

    def test_from_baseline_gate_closed(self):
        gate = ExpansionGate.from_baseline()
        result = gate.evaluate()
        assert not result.enabled
        assert len(result.blocking_conditions) >= 4  # all four fail at baseline

    def test_from_target_gate_open(self):
        gate = ExpansionGate.from_target()
        result = gate.evaluate()
        assert result.enabled
        assert result.blocking_conditions == []


class TestExpansionGateEvaluate:
    def test_all_thresholds_met_gate_open(self):
        result = _gate().evaluate()
        assert result.enabled
        assert not result.blocking_conditions

    def test_low_gi_blocks(self):
        result = _gate(gi=0.79).evaluate()
        assert not result.enabled
        assert any("Governance Integrity" in c for c in result.blocking_conditions)

    def test_low_lp_blocks(self):
        result = _gate(lp=0.79).evaluate()
        assert not result.enabled
        assert any("Least-Privilege" in c for c in result.blocking_conditions)

    def test_zero_deny_rate_blocks(self):
        result = _gate(deny=0.0).evaluate()
        assert not result.enabled
        assert any("DenyRate_guarded" in c for c in result.blocking_conditions)

    def test_low_audit_coverage_blocks(self):
        result = _gate(audit=0.94).evaluate()
        assert not result.enabled
        assert any("AuditCoverage" in c for c in result.blocking_conditions)

    def test_multiple_failures_reported(self):
        result = _gate(gi=0.5, lp=0.5, deny=0.0, audit=0.5).evaluate()
        assert not result.enabled
        assert len(result.blocking_conditions) == 4

    def test_effective_quality_computed(self):
        gate = _gate(gi=0.85, lp=0.88)
        result = gate.evaluate()
        expected = BASELINE_AP * 0.85 * 0.88
        assert result.effective_quality == pytest.approx(expected, abs=1e-3)


class TestGateResult:
    def test_summary_open(self):
        r = _gate().evaluate()
        assert "GATE OPEN" in r.summary

    def test_summary_closed(self):
        r = _gate(gi=0.5).evaluate()
        assert "GATE CLOSED" in r.summary
        assert "Governance Integrity" in r.summary

    def test_enabled_property(self):
        r = GateResult(
            enabled=True,
            governance_integrity=0.85,
            least_privilege=0.88,
            deny_rate_guarded=0.1,
            audit_coverage=0.97,
        )
        assert r.enabled

    def test_thresholds_are_blueprint_values(self):
        assert _GI_THRESHOLD == 0.80
        assert _LP_THRESHOLD == 0.80
        assert _AUDIT_COVERAGE_THRESHOLD == 0.95
