"""
Tests for Phase 6 — Safe Autonomy Expansion Gate
(src/codex/autonomy/expansion_gate.py)
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from codex.autonomy.expansion_gate import (
    _AUDIT_COVERAGE_THRESHOLD,
    _GI_THRESHOLD,
    _LP_THRESHOLD,
    BASELINE_AP,
    BASELINE_GI,
    BASELINE_LP,
    BASELINE_Q,
    MEASURED_AUDIT_COVERAGE,
    MEASURED_DENY_RATE,
    MEASURED_GI,
    MEASURED_LP,
    MEASURED_Q,
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
        assert BASELINE_AP == pytest.approx(0.877), "BASELINE_AP is not valid"
        assert BASELINE_GI == pytest.approx(0.5405), "BASELINE_GI is not valid"
        assert BASELINE_LP == pytest.approx(0.57), "BASELINE_LP is not valid"
        assert BASELINE_Q == pytest.approx(BASELINE_AP * BASELINE_GI * BASELINE_LP, abs=1e-3)

    def test_target_quality_matches_blueprint(self):
        expected = BASELINE_AP * TARGET_GI * TARGET_LP
        assert TARGET_Q == pytest.approx(expected, abs=1e-3)
        assert TARGET_Q > 0.6, "TARGET_Q must be greater than zero"

    def test_from_baseline_gate_closed(self):
        gate = ExpansionGate.from_baseline()
        result = gate.evaluate()
        assert not result.enabled, "Result must not be empty"
        assert len(result.blocking_conditions) >= 4, "Collection must not be empty"

    def test_from_target_gate_open(self):
        gate = ExpansionGate.from_target()
        result = gate.evaluate()
        assert result.enabled, "Result must not be empty"
        assert result.blocking_conditions == [], "Result must not be empty"


class TestExpansionGateEvaluate:
    def test_all_thresholds_met_gate_open(self):
        result = _gate().evaluate()
        assert result.enabled, "Result must not be empty"
        assert not result.blocking_conditions, "Result must not be empty"

    def test_low_gi_blocks(self):
        result = _gate(gi=0.79).evaluate()
        assert not result.enabled, "Result must not be empty"
        assert any("Governance Integrity" in c for c in result.blocking_conditions), "Result must not be empty"

    def test_low_lp_blocks(self):
        result = _gate(lp=0.79).evaluate()
        assert not result.enabled, "Result must not be empty"
        assert any("Least-Privilege" in c for c in result.blocking_conditions), "Result must not be empty"

    def test_zero_deny_rate_blocks(self):
        result = _gate(deny=0.0).evaluate()
        assert not result.enabled, "Result must not be empty"
        assert any("DenyRate_guarded" in c for c in result.blocking_conditions), "Result must not be empty"

    def test_low_audit_coverage_blocks(self):
        result = _gate(audit=0.94).evaluate()
        assert not result.enabled, "Result must not be empty"
        assert any("AuditCoverage" in c for c in result.blocking_conditions), "Result must not be empty"

    def test_multiple_failures_reported(self):
        result = _gate(gi=0.5, lp=0.5, deny=0.0, audit=0.5).evaluate()
        assert not result.enabled, "Result must not be empty"
        assert len(result.blocking_conditions) == 4, "Collection must not be empty"

    def test_effective_quality_computed(self):
        gate = _gate(gi=0.85, lp=0.88)
        result = gate.evaluate()
        expected = BASELINE_AP * 0.85 * 0.88
        assert result.effective_quality == pytest.approx(expected, abs=1e-3)


class TestGateResult:
    def test_summary_open(self):
        r = _gate().evaluate()
        assert "GATE OPEN" in r.summary, "Condition must be true"

    def test_summary_closed(self):
        r = _gate(gi=0.5).evaluate()
        assert "GATE CLOSED" in r.summary, "Condition must be true"
        assert "Governance Integrity" in r.summary, "Condition must be true"

    def test_enabled_property(self):
        r = GateResult(
            enabled=True,
            governance_integrity=0.85,
            least_privilege=0.88,
            deny_rate_guarded=0.1,
            audit_coverage=0.97,
        )
        assert r.enabled, "Condition must be true"

    def test_thresholds_are_blueprint_values(self):
        assert _GI_THRESHOLD == 0.80, "_GI_THRESHOLD is not valid"
        assert _LP_THRESHOLD == 0.80, "_LP_THRESHOLD is not valid"
        assert _AUDIT_COVERAGE_THRESHOLD == 0.95, "_AUDIT_COVERAGE_THRESHOLD is not valid"


class TestExpansionGateMeasured:
    """Post Phase 1-5 + entry-point wiring — gate must open."""

    def test_from_measured_gate_open(self):
        """from_measured() must produce an open gate (all 4 conditions met)."""
        result = ExpansionGate.from_measured().evaluate()
        assert (result.enabled, "Result must not be empty"
        ), f"Phase 1-5 measured gate is CLOSED — blocking: {result.blocking_conditions}"

    def test_measured_gi_at_target(self):
        assert MEASURED_GI >= TARGET_GI, "MEASURED_GI must be greater than zero"

    def test_measured_lp_at_target(self):
        assert MEASURED_LP >= TARGET_LP, "MEASURED_LP must be greater than zero"

    def test_measured_deny_rate_positive(self):
        assert MEASURED_DENY_RATE > 0.0, "MEASURED_DENY_RATE must be greater than zero"

    def test_measured_audit_coverage_above_threshold(self):
        assert MEASURED_AUDIT_COVERAGE >= _AUDIT_COVERAGE_THRESHOLD, "MEASURED_AUDIT_COVERAGE must be greater than zero"

    def test_measured_q_above_baseline(self):
        """Effective quality must improve over baseline."""
        assert MEASURED_Q > BASELINE_Q, "MEASURED_Q must be greater than zero"

    def test_measured_constants_consistent(self):
        assert MEASURED_Q == pytest.approx(BASELINE_AP * MEASURED_GI * MEASURED_LP, abs=1e-3)


class TestAutonomyGateCheckScript:
    """Tests for scripts/ci/autonomy_gate_check.py CLI."""

    def test_gate_check_permitted(self, tmp_path):
        """Gate allows ADVISORY_WRITE under SAFE_AUTO mode (requires ASSISTED)."""
        result = subprocess.run(
            [
                sys.executable,
                "scripts/ci/autonomy_gate_check.py",
                "--surface",
                "AUT-007",
                "--class",
                "ADVISORY_WRITE",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "Result must not be empty"

    def test_gate_check_no_fail_flag(self, tmp_path):
        """--no-fail makes even a denial exit 0."""
        registry_file = tmp_path / "reg.yaml"
        registry_file.write_text(
            "schema_version: '1.0.0'\n" "autonomy_mode: OFF\n" "kill_switch: false\n"
        )
        env = {**os.environ, "CODEX_AUTONOMY_REGISTRY": str(registry_file)}
        result = subprocess.run(
            [
                sys.executable,
                "scripts/ci/autonomy_gate_check.py",
                "--surface",
                "AUT-007",
                "--class",
                "ADVISORY_WRITE",
                "--no-fail",
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, "Result must not be empty"
