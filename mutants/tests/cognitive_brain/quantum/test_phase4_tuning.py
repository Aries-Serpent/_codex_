"""
Phase 4.5 Tuning Hook Tests — Quantum Compliance System

Tests for:
- _is_tuning_enabled(): env flag detection
- _detect_pattern(): heuristic pattern classification
- _extract_bayesian_evidence(): evidence dict from AuditResult
- _apply_poc_tuning(): probability boosting + renormalisation
- Graceful degradation on missing / corrupt tuning rules file
- EXP1BResults.k1_verified field population
"""

import json

from cognitive_brain.integrations.compliance_integration import (
    AuditResult,
    ComplianceDecision,
    QuantumComplianceAssessor,
)
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.config import QuantumConfig

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_assessor(lightweight: bool = True) -> QuantumComplianceAssessor:
    """Build a minimal QuantumComplianceAssessor suitable for unit tests."""
    from cognitive_brain.models.quantum_metrics import QuantumMetricRepository

    config = QuantumConfig()
    repo = QuantumMetricRepository()
    monitor = CoherenceMonitor(config, repo)
    return QuantumComplianceAssessor(config=config, monitor=monitor, repository=repo)


def _make_audit(**kwargs) -> AuditResult:
    """Build an AuditResult with sensible defaults, overriding with kwargs."""
    defaults = dict(
        audit_id="test-001",
        risk_level="medium",
        remediation_cost=5000.0,
        score=0.75,
        business_impact=0.5,
        violation_count=2,
        pii_indicators=0,
    )
    defaults.update(kwargs)
    return AuditResult(**defaults)


# ---------------------------------------------------------------------------
# TestIsTuningEnabled
# ---------------------------------------------------------------------------


class TestIsTuningEnabled:
    """Tests for QuantumComplianceAssessor._is_tuning_enabled()."""

    def test_disabled_by_default(self, monkeypatch):
        monkeypatch.delenv("CODEX_BAYESIAN_MODE", raising=False)
        monkeypatch.delenv("CODEX_FUZZY_MODE", raising=False)
        assessor = _make_assessor()
        assert assessor._is_tuning_enabled() is False, "assess is not valid"

    def test_bayesian_mode_enables_tuning(self, monkeypatch):
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "true")
        monkeypatch.delenv("CODEX_FUZZY_MODE", raising=False)
        assessor = _make_assessor()
        assert assessor._is_tuning_enabled() is True, "assess is not valid"

    def test_fuzzy_mode_enables_tuning(self, monkeypatch):
        monkeypatch.delenv("CODEX_BAYESIAN_MODE", raising=False)
        monkeypatch.setenv("CODEX_FUZZY_MODE", "true")
        assessor = _make_assessor()
        assert assessor._is_tuning_enabled() is True, "assess is not valid"

    def test_both_modes_enables_tuning(self, monkeypatch):
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "true")
        monkeypatch.setenv("CODEX_FUZZY_MODE", "true")
        assessor = _make_assessor()
        assert assessor._is_tuning_enabled() is True, "assess is not valid"

    def test_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "TRUE")
        assessor = _make_assessor()
        assert assessor._is_tuning_enabled() is True, "assess is not valid"


# ---------------------------------------------------------------------------
# TestDetectPattern
# ---------------------------------------------------------------------------


class TestDetectPattern:
    """Tests for QuantumComplianceAssessor._detect_pattern()."""

    def setup_method(self):
        self.assessor = _make_assessor()

    def test_pattern_H_high_score(self):
        audit = _make_audit(score=0.97, risk_level="medium", violation_count=0, pii_indicators=0)
        assert self.assessor._detect_pattern(audit) == "H", "Condition must be true"

    def test_pattern_H_exact_boundary(self):
        audit = _make_audit(score=0.95, violation_count=0, pii_indicators=0)
        assert self.assessor._detect_pattern(audit) == "H", "Condition must be true"

    def test_pattern_F_multi_violation(self):
        audit = _make_audit(
            score=0.70, violation_count=5, business_impact=0.80, remediation_cost=4000
        )
        assert self.assessor._detect_pattern(audit) == "F", "Condition must be true"

    def test_pattern_F_requires_all_conditions(self):
        # violation_count=5 but impact too low → no Pattern F
        audit = _make_audit(
            score=0.70, violation_count=5, business_impact=0.50, remediation_cost=4000
        )
        assert self.assessor._detect_pattern(audit) != "F", "Condition must be true"

    def test_pattern_E_pii_indicators(self):
        audit = _make_audit(score=0.60, pii_indicators=3, risk_level="medium")
        assert self.assessor._detect_pattern(audit) == "E", "Condition must be true"

    def test_pattern_E_high_risk_with_pii(self):
        audit = _make_audit(score=0.60, pii_indicators=1, risk_level="high")
        assert self.assessor._detect_pattern(audit) == "E", "Condition must be true"

    def test_pattern_C_medium_boundary(self):
        audit = _make_audit(score=0.70, risk_level="medium", violation_count=1, pii_indicators=0)
        assert self.assessor._detect_pattern(audit) == "C", "Condition must be true"

    def test_no_pattern_match(self):
        audit = _make_audit(score=0.50, risk_level="low", violation_count=1, pii_indicators=0)
        assert self.assessor._detect_pattern(audit) is None, "Condition must be true"

    def test_H_takes_priority_over_C(self):
        # score=0.96 would match C boundary but H threshold (≥0.95) should win
        audit = _make_audit(score=0.96, risk_level="medium", violation_count=0, pii_indicators=0)
        assert self.assessor._detect_pattern(audit) == "H", "Condition must be true"


# ---------------------------------------------------------------------------
# TestExtractBayesianEvidence
# ---------------------------------------------------------------------------


class TestExtractBayesianEvidence:
    """Tests for QuantumComplianceAssessor._extract_bayesian_evidence()."""

    def setup_method(self):
        self.assessor = _make_assessor()

    def test_all_true_case(self):
        audit = _make_audit(
            score=0.90,
            risk_level="high",
            remediation_cost=15000,
            business_impact=0.80,
            pii_indicators=2,
            violation_count=6,
        )
        ev = self.assessor._extract_bayesian_evidence(audit)
        assert ev["high_score"] == "true", "Condition must be true"
        assert ev["high_risk"] == "true", "Condition must be true"
        assert ev["expensive"] == "true", "Condition must be true"
        assert ev["high_impact"] == "true", "Condition must be true"
        assert ev["has_pii"] == "true", "Condition must be true"
        assert ev["multi_violation"] == "true", "Condition must be true"

    def test_all_false_case(self):
        audit = _make_audit(
            score=0.50, risk_level="low", remediation_cost=1000, business_impact=0.30
        )
        ev = self.assessor._extract_bayesian_evidence(audit)
        assert ev["high_score"] == "false", "Condition must be true"
        assert ev["high_risk"] == "false", "Condition must be true"
        assert ev["expensive"] == "false", "Condition must be true"
        assert ev["has_pii"] == "false", "Condition must be true"

    def test_string_values(self):
        audit = _make_audit(score=0.85)
        ev = self.assessor._extract_bayesian_evidence(audit)
        for v in ev.values():
            assert v in ("true", "false"), f"Unexpected value: {v!r}"


# ---------------------------------------------------------------------------
# TestApplyPocTuning
# ---------------------------------------------------------------------------


class TestApplyPocTuning:
    """Tests for QuantumComplianceAssessor._apply_poc_tuning()."""

    def setup_method(self):
        self.assessor = _make_assessor()
        self.decision_names = [
            "APPROVE",
            "APPROVE_WITH_MONITORING",
            "REJECT",
            "CONDITIONAL_APPROVAL",
        ]

    def test_no_change_when_tuning_disabled(self, monkeypatch):
        monkeypatch.delenv("CODEX_BAYESIAN_MODE", raising=False)
        monkeypatch.delenv("CODEX_FUZZY_MODE", raising=False)
        probs = [0.1, 0.5, 0.3, 0.1]
        audit = _make_audit(score=0.96)
        result = self.assessor._apply_poc_tuning(probs, audit, self.decision_names)
        assert result == probs, "Result must not be empty"

    def test_bayesian_boost_on_pattern_H(self, monkeypatch, tmp_path):
        """Pattern H with high_score=True should boost APPROVE_WITH_MONITORING."""
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "true")
        monkeypatch.delenv("CODEX_FUZZY_MODE", raising=False)

        # Write a simple tuning rules file
        rules = {
            "H": {
                "bayesian": [
                    {
                        "evidence": {"high_score": "true"},
                        "target_node": "decision",
                        "target_value": "APPROVE_WITH_MONITORING",
                        "effect": 1.4,
                    }
                ],
                "fuzzy": {},
            }
        }
        rules_path = tmp_path / "target_patterns.json"
        rules_path.write_text(json.dumps(rules))

        # Patch the assessor's cache with the test rules
        self.assessor._tuning_rules_cache = rules

        probs = [0.4, 0.2, 0.3, 0.1]  # APPROVE highest initially
        audit = _make_audit(score=0.97, pii_indicators=0, violation_count=0)

        result = self.assessor._apply_poc_tuning(probs, audit, self.decision_names)

        # APPROVE_WITH_MONITORING (index 1) should be boosted
        assert result[1] > probs[1] / sum(probs), "Value must be greater than zero"
        # Probabilities must be normalised
        assert abs(sum(result) - 1.0) < 1e-9, "Result must not be empty"

    def test_probabilities_renormalised(self, monkeypatch):
        """After tuning, probabilities must still sum to 1.0."""
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "true")
        rules = {
            "H": {
                "bayesian": [
                    {
                        "evidence": {"high_score": "true"},
                        "target_node": "decision",
                        "target_value": "APPROVE_WITH_MONITORING",
                        "effect": 2.0,
                    }
                ],
                "fuzzy": {},
            }
        }
        self.assessor._tuning_rules_cache = rules
        probs = [0.25, 0.25, 0.25, 0.25]
        audit = _make_audit(score=0.97, pii_indicators=0, violation_count=0)
        result = self.assessor._apply_poc_tuning(probs, audit, self.decision_names)
        assert abs(sum(result) - 1.0) < 1e-9, "Result must not be empty"

    def test_graceful_degradation_on_bad_rules(self, monkeypatch):
        """Corrupt rules file → return original probabilities unchanged."""
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "true")
        self.assessor._tuning_rules_cache = None  # force reload

        probs = [0.1, 0.5, 0.3, 0.1]
        audit = _make_audit(score=0.97, pii_indicators=0, violation_count=0)

        # Point to a non-existent file — _load_tuning_rules returns {}
        with monkeypatch.context() as m:
            m.setattr(self.assessor, "_load_tuning_rules", lambda: {})
            result = self.assessor._apply_poc_tuning(probs, audit, self.decision_names)

        # No tuning for this pattern → returns original
        assert result == probs, "Result must not be empty"

    def test_no_pattern_match_returns_unchanged(self, monkeypatch):
        """Audit that matches no known pattern → return original probabilities."""
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "true")
        rules = {"H": {"bayesian": [], "fuzzy": {}}}
        self.assessor._tuning_rules_cache = rules
        probs = [0.25, 0.25, 0.25, 0.25]
        # score=0.50, low risk, no PII → no pattern match
        audit = _make_audit(score=0.50, risk_level="low")
        result = self.assessor._apply_poc_tuning(probs, audit, self.decision_names)
        assert result == probs, "Result must not be empty"


# ---------------------------------------------------------------------------
# TestTuningEndToEnd
# ---------------------------------------------------------------------------


class TestTuningEndToEnd:
    """End-to-end test: tuning changes the compliance decision for Pattern H."""

    def test_pattern_H_decision_with_bayesian_tuning(self, monkeypatch):
        """
        Pattern H scenario (score=0.97) normally resolves to APPROVE.
        With Bayesian tuning (APPROVE_WITH_MONITORING ×1.5) the decision
        should shift to APPROVE_WITH_MONITORING.
        """
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "true")
        monkeypatch.delenv("CODEX_FUZZY_MODE", raising=False)

        assessor = _make_assessor(lightweight=False)

        # Inject strong rule that guarantees APPROVE_WITH_MONITORING wins for H
        assessor._tuning_rules_cache = {
            "H": {
                "bayesian": [
                    {
                        "evidence": {"high_score": "true"},
                        "target_node": "decision",
                        "target_value": "APPROVE_WITH_MONITORING",
                        "effect": 3.0,  # Strong boost
                    }
                ],
                "fuzzy": {},
            }
        }

        audit = _make_audit(
            audit_id="h-tuning-test",
            score=0.97,
            risk_level="medium",
            remediation_cost=3000.0,
            business_impact=0.60,
            pii_indicators=0,
            violation_count=0,
        )
        assessment = assessor.assess_compliance(audit)
        # With 3x boost on APPROVE_WITH_MONITORING, it should win
        assert assessment.decision == ComplianceDecision.APPROVE_WITH_MONITORING, "decision is not valid"

    def test_full_pipeline_no_regression_tuning_off(self, monkeypatch):
        """With tuning disabled, assess_compliance produces consistent results."""
        monkeypatch.delenv("CODEX_BAYESIAN_MODE", raising=False)
        monkeypatch.delenv("CODEX_FUZZY_MODE", raising=False)

        assessor = _make_assessor(lightweight=False)
        audit = _make_audit(score=0.90, risk_level="low", remediation_cost=1000.0)

        result1 = assessor.assess_compliance(audit)
        result2 = assessor.assess_compliance(audit)
        # Same input → same decision (deterministic)
        assert result1.decision == result2.decision, "Result must not be empty"


# ---------------------------------------------------------------------------
# TestK1VerifiedField
# ---------------------------------------------------------------------------


class TestK1VerifiedField:
    """Tests for EXP1BResults.k1_verified field introduced in Phase 4.5."""

    def test_k1_verified_populated_in_verified_mode(self):
        """When use_verified_labels=True, k1_verified should be set (== k1)."""

        from cognitive_brain.experiments.exp1b_revalidation import (
            run_exp1b_revalidation,
        )

        result = run_exp1b_revalidation(scenarios=20, seed=42, use_verified_labels=True)
        assert hasattr(result, "k1_verified")
        assert result.k1_verified == result.k1, "Result must not be empty"

    def test_k1_verified_zero_in_raw_mode(self):
        """When use_verified_labels=False, k1_verified should be 0.0."""

        from cognitive_brain.experiments.exp1b_revalidation import (
            run_exp1b_revalidation,
        )

        result = run_exp1b_revalidation(scenarios=20, seed=42, use_verified_labels=False)
        assert result.k1_verified == 0.0, "Result must not be empty"

    def test_load_tuning_rules_returns_dict(self):
        """_load_tuning_rules() returns a dict (possibly empty) without raising."""
        assessor = _make_assessor()
        assessor._tuning_rules_cache = None  # force reload
        rules = assessor._load_tuning_rules()
        assert isinstance(rules, dict)
