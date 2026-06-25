"""
Phase 5 Cognitive Brain Interface Tests

Tests for:
- CognitiveBrain.create()
- CognitiveBrain.decide() — happy path, session memory, fallback
- CognitiveBrain.get_cognitive_state()
- CognitiveBrain.get_health()
- CognitiveBrain.explain()
- _generate_agent_hints()  (all four decision branches)
- _detect_pattern_from_inputs() (all patterns + default)
- _inputs_to_audit()
"""

from cognitive_brain.agents.cognitive_interface import (
    AgentHealthSnapshot,
    CognitiveBrain,
    CognitiveDecision,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_brain(enable_memory: bool = True) -> CognitiveBrain:
    return CognitiveBrain.create(enable_memory=enable_memory)


def _approve_inputs() -> dict:
    return {"score": 0.92, "risk_level": "low", "remediation_cost": 1500.0, "business_impact": 0.8}


def _monitor_inputs() -> dict:
    return {
        "score": 0.82,
        "risk_level": "medium",
        "remediation_cost": 8000.0,
        "business_impact": 0.6,
    }


def _reject_inputs() -> dict:
    return {
        "score": 0.40,
        "risk_level": "high",
        "remediation_cost": 20000.0,
        "business_impact": 0.3,
    }


def _conditional_inputs() -> dict:
    return {
        "score": 0.65,
        "risk_level": "medium",
        "remediation_cost": 5500.0,
        "business_impact": 0.5,
    }


# ---------------------------------------------------------------------------
# TestCognitiveBrainCreate
# ---------------------------------------------------------------------------


class TestCognitiveBrainCreate:
    def test_create_returns_brain(self):
        brain = _make_brain()
        assert isinstance(brain, CognitiveBrain)

    def test_enable_memory_true(self):
        brain = CognitiveBrain.create(enable_memory=True)
        assert brain._enable_memory is True

    def test_enable_memory_false(self):
        brain = CognitiveBrain.create(enable_memory=False)
        assert brain._enable_memory is False


# ---------------------------------------------------------------------------
# TestCognitiveBrainDecide
# ---------------------------------------------------------------------------


class TestCognitiveBrainDecide:
    def test_decide_returns_cognitive_decision(self):
        brain = _make_brain()
        result = brain.decide("compliance_audit", _approve_inputs())
        assert isinstance(result, CognitiveDecision)

    def test_decide_decision_is_valid_string(self):
        brain = _make_brain()
        result = brain.decide("compliance_audit", _approve_inputs())
        assert result.decision in {
            "approve",
            "approve_with_monitoring",
            "reject",
            "conditional_approval",
        }

    def test_decide_confidence_in_range(self):
        brain = _make_brain()
        result = brain.decide("compliance_audit", _conditional_inputs())
        assert 0.0 <= result.confidence <= 1.0

    def test_decide_coherence_in_range(self):
        brain = _make_brain()
        result = brain.decide("compliance_audit", _monitor_inputs())
        assert 0.0 <= result.coherence <= 1.0

    def test_decide_reasoning_nonempty(self):
        brain = _make_brain()
        result = brain.decide("compliance_audit", _reject_inputs())
        assert isinstance(result.reasoning, str) and len(result.reasoning) > 0

    def test_decide_agent_hints_nonempty(self):
        brain = _make_brain()
        result = brain.decide("compliance_audit", _approve_inputs())
        assert isinstance(result.agent_hints, dict)
        assert "next_action" in result.agent_hints

    def test_decide_alternatives_is_list(self):
        brain = _make_brain()
        result = brain.decide("compliance_audit", _approve_inputs())
        assert isinstance(result.alternatives, list)
        assert len(result.alternatives) >= 1

    def test_decide_cognitive_state_has_context(self):
        brain = _make_brain()
        result = brain.decide("risk_review", _approve_inputs())
        assert result.cognitive_state["context"] == "risk_review"

    def test_decide_stores_session_memory(self):
        brain = _make_brain()
        brain.decide("compliance_audit", _approve_inputs(), session_id="sess-001")
        assert "sess-001" in brain._memory

    def test_decide_no_memory_when_disabled(self):
        brain = CognitiveBrain.create(enable_memory=False)
        brain.decide("compliance_audit", _approve_inputs(), session_id="sess-999")
        assert "sess-999" not in brain._memory

    def test_decide_increments_history(self):
        brain = _make_brain()
        brain.decide("compliance_audit", _approve_inputs(), session_id="s1")
        brain.decide("compliance_audit", _monitor_inputs(), session_id="s2")
        assert len(brain._history) == 2


# ---------------------------------------------------------------------------
# TestCognitiveBrainGetState
# ---------------------------------------------------------------------------


class TestCognitiveBrainGetState:
    def test_get_state_returns_dict_after_decide(self):
        brain = _make_brain()
        brain.decide("compliance_audit", _approve_inputs(), session_id="abc")
        state = brain.get_cognitive_state("abc")
        assert isinstance(state, dict)
        assert state["session_id"] == "abc"

    def test_get_state_returns_none_unknown_session(self):
        brain = _make_brain()
        assert brain.get_cognitive_state("does-not-exist") is None

    def test_get_state_returns_none_when_memory_disabled(self):
        brain = CognitiveBrain.create(enable_memory=False)
        brain.decide("compliance_audit", _approve_inputs(), session_id="xyz")
        assert brain.get_cognitive_state("xyz") is None


# ---------------------------------------------------------------------------
# TestCognitiveBrainHealth
# ---------------------------------------------------------------------------


class TestCognitiveBrainHealth:
    def test_health_returns_snapshot(self):
        brain = _make_brain()
        health = brain.get_health()
        assert isinstance(health, AgentHealthSnapshot)

    def test_health_status_healthy_on_new_brain(self):
        brain = _make_brain()
        assert brain.get_health().health_status == "healthy"

    def test_health_decision_count_updates(self):
        brain = _make_brain()
        brain.decide("test", _approve_inputs(), session_id="h1")
        brain.decide("test", _approve_inputs(), session_id="h2")
        assert brain.get_health().decision_count == 2

    def test_health_error_count_zero_initially(self):
        brain = _make_brain()
        assert brain.get_health().error_count == 0


# ---------------------------------------------------------------------------
# TestCognitiveBrainExplain
# ---------------------------------------------------------------------------


class TestCognitiveBrainExplain:
    def test_explain_agent_returns_json(self):
        import json

        brain = _make_brain()
        decision = brain.decide("compliance_audit", _approve_inputs())
        explanation = brain.explain(decision, audience="agent")
        data = json.loads(explanation)
        assert "decision" in data
        assert "confidence" in data

    def test_explain_human_returns_string(self):
        brain = _make_brain()
        decision = brain.decide("compliance_audit", _approve_inputs())
        explanation = brain.explain(decision, audience="human")
        assert isinstance(explanation, str) and len(explanation) > 0


# ---------------------------------------------------------------------------
# TestAgentHints
# ---------------------------------------------------------------------------


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
        assert hints["next_action"] == "escalate_to_human_reviewer"

    def test_hints_monitor_setup(self):
        class _FakeAssessment:
            decision = type("D", (), {"value": "approve_with_monitoring"})()
            coherence = 0.8
            confidence = 0.85
            reasoning = "test"
            used_superposition = True
            evaluation_time_ms = 5.0

        hints = CognitiveBrain._generate_agent_hints(_FakeAssessment(), "test")
        assert hints["next_action"] == "setup_monitoring_alerts"
        assert hints["auto_approve_allowed"] == "no"

    def test_hints_conditional_evidence_request(self):
        class _FakeAssessment:
            decision = type("D", (), {"value": "conditional_approval"})()
            coherence = 0.75
            confidence = 0.70
            reasoning = "test"
            used_superposition = False
            evaluation_time_ms = 5.0

        hints = CognitiveBrain._generate_agent_hints(_FakeAssessment(), "test")
        assert hints["next_action"] == "request_additional_evidence"

    def test_hints_approve_finalize(self):
        class _FakeAssessment:
            decision = type("D", (), {"value": "approve"})()
            coherence = 0.9
            confidence = 0.97
            reasoning = "test"
            used_superposition = True
            evaluation_time_ms = 4.0

        hints = CognitiveBrain._generate_agent_hints(_FakeAssessment(), "test")
        assert hints["next_action"] == "finalize_approval"
        assert hints["auto_approve_allowed"] == "yes"

    def test_hints_coherence_warning(self):
        class _FakeAssessment:
            decision = type("D", (), {"value": "approve"})()
            coherence = 0.60  # below threshold
            confidence = 0.9
            reasoning = "test"
            used_superposition = False
            evaluation_time_ms = 5.0

        hints = CognitiveBrain._generate_agent_hints(_FakeAssessment(), "test")
        assert hints.get("health_warning") == "coherence_below_threshold"


# ---------------------------------------------------------------------------
# TestPatternDetection
# ---------------------------------------------------------------------------


class TestPatternDetection:
    def test_pattern_h_high_score(self):
        inputs = {"score": 0.96, "risk_level": "medium", "violation_count": 0, "pii_indicators": 0}
        assert CognitiveBrain._detect_pattern_from_inputs(inputs) == "H"

    def test_pattern_f_violation_count(self):
        inputs = {"score": 0.70, "risk_level": "medium", "violation_count": 6, "pii_indicators": 0}
        assert CognitiveBrain._detect_pattern_from_inputs(inputs) == "F"

    def test_pattern_e_pii(self):
        inputs = {"score": 0.60, "risk_level": "medium", "violation_count": 1, "pii_indicators": 2}
        assert CognitiveBrain._detect_pattern_from_inputs(inputs) == "E"

    def test_pattern_c_medium_zone(self):
        inputs = {"score": 0.65, "risk_level": "medium", "violation_count": 0, "pii_indicators": 0}
        assert CognitiveBrain._detect_pattern_from_inputs(inputs) == "C"

    def test_pattern_none_no_match(self):
        inputs = {"score": 0.80, "risk_level": "high", "violation_count": 0, "pii_indicators": 0}
        assert CognitiveBrain._detect_pattern_from_inputs(inputs) is None
