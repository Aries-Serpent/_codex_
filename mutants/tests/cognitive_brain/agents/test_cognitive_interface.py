#         assert result.decision in {, "Result must not be empty"
# Phase 5 Cognitive Brain Interface Tests
# - CognitiveBrain.decide() — happy path, session memory, fallback
# - CognitiveBrain.get_cognitive_state()
# - CognitiveBrain.get_health()
# - CognitiveBrain.explain()
# - _generate_agent_hints()  (all four decision branches)
# - _detect_pattern_from_inputs() (all patterns + default)
# - _inputs_to_audit()
# 

class TestAgentHints:
    """Verify agent hint content for each decision branch."""

    def test_hints_reject_escalation(self):
        # Force a reject via _generate_agent_hints directly
        class _FakeAssessment:
            decision = type("D", (), {"value": "reject"})()
            coherence = 0.7
            confidence = 0.9
            reasoning = "test"
            used_superposition = False
            evaluation_time_ms = 5.0

        hints = CognitiveBrain._generate_agent_hints(_FakeAssessment(), "test")
        assert hints["next_action"] == "escalate_to_human_reviewer", "Condition must be true"

    def test_hints_monitor_setup(self):
        class _FakeAssessment:
            decision = type("D", (), {"value": "approve_with_monitoring"})()
            coherence = 0.8
            confidence = 0.85
            reasoning = "test"
            used_superposition = True
            evaluation_time_ms = 5.0

        hints = CognitiveBrain._generate_agent_hints(_FakeAssessment(), "test")
        assert hints["next_action"] == "setup_monitoring_alerts", "Condition must be true"
        assert hints["auto_approve_allowed"] == "no", "Condition must be true"

    def test_hints_conditional_evidence_request(self):
        class _FakeAssessment:
            decision = type("D", (), {"value": "conditional_approval"})()
            coherence = 0.75
            confidence = 0.70
            reasoning = "test"
            used_superposition = False
            evaluation_time_ms = 5.0

        hints = CognitiveBrain._generate_agent_hints(_FakeAssessment(), "test")
        assert hints["next_action"] == "request_additional_evidence", "Condition must be true"

    def test_hints_approve_finalize(self):
        class _FakeAssessment:
            decision = type("D", (), {"value": "approve"})()
            coherence = 0.9
            confidence = 0.97
            reasoning = "test"
            used_superposition = True
            evaluation_time_ms = 4.0

        hints = CognitiveBrain._generate_agent_hints(_FakeAssessment(), "test")
        assert hints["next_action"] == "finalize_approval", "Condition must be true"
        assert hints["auto_approve_allowed"] == "yes", "Condition must be true"

    def test_hints_coherence_warning(self):
        class _FakeAssessment:
            decision = type("D", (), {"value": "approve"})()
            coherence = 0.60  # below threshold
            confidence = 0.9
            reasoning = "test"
            used_superposition = False
            evaluation_time_ms = 5.0

        hints = CognitiveBrain._generate_agent_hints(_FakeAssessment(), "test")
        assert hints.get("health_warning") == "coherence_below_threshold", "Condition must be true"


# ---------------------------------------------------------------------------
# TestPatternDetection
# ---------------------------------------------------------------------------


class TestPatternDetection:
    def test_pattern_h_high_score(self):
        inputs = {"score": 0.96, "risk_level": "medium", "violation_count": 0, "pii_indicators": 0}
        assert CognitiveBrain._detect_pattern_from_inputs(inputs) == "H", "Condition must be true"

    def test_pattern_f_violation_count(self):
        inputs = {"score": 0.70, "risk_level": "medium", "violation_count": 6, "pii_indicators": 0}
        assert CognitiveBrain._detect_pattern_from_inputs(inputs) == "F", "Condition must be true"

    def test_pattern_e_pii(self):
        inputs = {"score": 0.60, "risk_level": "medium", "violation_count": 1, "pii_indicators": 2}
        assert CognitiveBrain._detect_pattern_from_inputs(inputs) == "E", "Condition must be true"

    def test_pattern_c_medium_zone(self):
        inputs = {"score": 0.65, "risk_level": "medium", "violation_count": 0, "pii_indicators": 0}
        assert CognitiveBrain._detect_pattern_from_inputs(inputs) == "C", "Condition must be true"

    def test_pattern_none_no_match(self):
        inputs = {"score": 0.80, "risk_level": "high", "violation_count": 0, "pii_indicators": 0}
        assert CognitiveBrain._detect_pattern_from_inputs(inputs) is None, "Condition must be true"
