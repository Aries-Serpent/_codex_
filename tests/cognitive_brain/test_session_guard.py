"""Tests for SessionGuard — central session.create safety wrapper.

Covers:
- Unit: session config negotiated on create_session
- Unit: decision_id generated per invocation
- Unit: turn_id and task_id forwarded to result
- Unit: unsupported params stripped from safe_config
- Unit: fallback model selected when required capabilities not met
- Unit: telemetry event recorded (session_guard event_type)
- Integration: safe_create_session convenience wrapper
- Regression: haiku never receives reasoning_effort in safe_config
- Regression: all create_session paths produce model key in safe_config
"""

from __future__ import annotations

import pytest

from codex.cognitive_brain.session_guard import (
    SessionCreateResult,
    SessionGuard,
    get_default_guard,
    reset_default_guard,
    safe_create_session,
)
from codex.cognitive_brain.telemetry import CognitiveTelemetry, InMemoryTelemetryBackend

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def telemetry() -> CognitiveTelemetry:
    return CognitiveTelemetry(backends=[InMemoryTelemetryBackend()])


@pytest.fixture()
def guard(telemetry: CognitiveTelemetry) -> SessionGuard:
    return SessionGuard(telemetry=telemetry)


# ---------------------------------------------------------------------------
# Basic negotiation tests
# ---------------------------------------------------------------------------


class TestSessionGuardBasic:
    def test_returns_session_create_result(self, guard: SessionGuard) -> None:
        result = guard.create_session("claude-sonnet-5", {"max_tokens": 1024})
        assert isinstance(result, SessionCreateResult)

    def test_safe_config_has_model_key(self, guard: SessionGuard) -> None:
        result = guard.create_session("claude-haiku-4.5", {"max_tokens": 512})
        assert "model" in result.safe_config, "Result must not be empty"

    def test_resolved_model_in_result(self, guard: SessionGuard) -> None:
        result = guard.create_session("claude-haiku-4.5", {})
        assert result.resolved_model == "claude-haiku-4.5", "Result must not be empty"

    def test_decision_id_generated(self, guard: SessionGuard) -> None:
        result = guard.create_session("claude-haiku-4.5", {})
        assert result.decision_id, "Result must not be empty"
        assert len(result.decision_id) > 8, "Collection must not be empty"

    def test_two_calls_have_different_decision_ids(self, guard: SessionGuard) -> None:
        r1 = guard.create_session("claude-haiku-4.5", {})
        r2 = guard.create_session("claude-haiku-4.5", {})
        assert r1.decision_id != r2.decision_id, "decision_id is not valid"

    def test_duration_ms_recorded(self, guard: SessionGuard) -> None:
        result = guard.create_session("claude-haiku-4.5", {})
        assert result.duration_ms >= 0.0, "duration_ms must be greater than zero"


# ---------------------------------------------------------------------------
# Unsupported param stripping (key regression guard)
# ---------------------------------------------------------------------------


class TestSessionGuardParamStripping:
    def test_haiku_reasoning_effort_stripped(self, guard: SessionGuard) -> None:
        """Regression: claude-haiku-4.5 must not receive reasoning_effort."""
        result = guard.create_session(
            "claude-haiku-4.5",
            {"reasoning_effort": "high", "max_tokens": 2048},
        )
        assert "reasoning_effort" not in result.safe_config, "Result must not be empty"

    def test_haiku_thinking_stripped(self, guard: SessionGuard) -> None:
        result = guard.create_session(
            "claude-haiku-4.5",
            {"thinking": {"type": "enabled", "budget_tokens": 500}, "max_tokens": 1024},
        )
        assert "thinking" not in result.safe_config, "Result must not be empty"

    def test_sonnet_reasoning_effort_preserved(self, guard: SessionGuard) -> None:
        result = guard.create_session(
            "claude-sonnet-5",
            {"reasoning_effort": "medium", "max_tokens": 4096},
        )
        assert "reasoning_effort" in result.safe_config, "Result must not be empty"

    def test_stripped_params_reported(self, guard: SessionGuard) -> None:
        result = guard.create_session(
            "claude-haiku-4.5",
            {"reasoning_effort": "high"},
        )
        assert "reasoning_effort" in result.params_stripped, "Result must not be empty"

    def test_passthrough_params_preserved(self, guard: SessionGuard) -> None:
        result = guard.create_session(
            "claude-haiku-4.5",
            {"max_tokens": 1024, "temperature": 0.3},
        )
        assert result.safe_config.get("max_tokens") == 1024, "Result must not be empty"
        assert result.safe_config.get("temperature") == 0.3, "Result must not be empty"


# ---------------------------------------------------------------------------
# Fallback model selection
# ---------------------------------------------------------------------------


class TestSessionGuardFallback:
    def test_fallback_selected_for_unmet_capabilities(self) -> None:
        """A model without reasoning_effort should trigger a fallback."""
        guard = SessionGuard()
        result = guard.create_session(
            "claude-haiku-4.5",
            {"max_tokens": 1024},
            required_capabilities=["reasoning_effort"],
        )
        # Fallback must have been used since haiku can't do reasoning_effort.
        assert result.fallback_used is True, "Result must not be empty"
        assert result.resolved_model != "claude-haiku-4.5", "Result must not be empty"

    def test_no_fallback_when_model_meets_requirements(self) -> None:
        guard = SessionGuard()
        result = guard.create_session(
            "claude-sonnet-5",
            {"reasoning_effort": "low"},
            required_capabilities=["reasoning_effort"],
        )
        assert result.fallback_used is False, "Result must not be empty"


# ---------------------------------------------------------------------------
# Turn/task ID forwarding
# ---------------------------------------------------------------------------


class TestTurnTaskId:
    def test_turn_id_forwarded(self, guard: SessionGuard) -> None:
        result = guard.create_session("claude-haiku-4.5", {}, turn_id="turn-42")
        assert result.turn_id == "turn-42", "Result must not be empty"

    def test_task_id_forwarded(self, guard: SessionGuard) -> None:
        result = guard.create_session("claude-haiku-4.5", {}, task_id="task-7")
        assert result.task_id == "task-7", "Result must not be empty"

    def test_turn_and_task_id_none_by_default(self, guard: SessionGuard) -> None:
        result = guard.create_session("claude-haiku-4.5", {})
        assert result.turn_id is None, "Result must not be empty"
        assert result.task_id is None, "Result must not be empty"


# ---------------------------------------------------------------------------
# Telemetry integration
# ---------------------------------------------------------------------------


class TestSessionGuardTelemetry:
    def test_session_guard_event_emitted(
        self, guard: SessionGuard, telemetry: CognitiveTelemetry
    ) -> None:
        guard.create_session("claude-haiku-4.5", {"reasoning_effort": "high"})
        events = telemetry.query(event_type="session_guard")
        assert len(events) >= 1, "Events must not be empty"

    def test_session_guard_event_has_decision_id(
        self, guard: SessionGuard, telemetry: CognitiveTelemetry
    ) -> None:
        guard.create_session("claude-haiku-4.5", {})
        events = telemetry.query(event_type="session_guard")
        assert events[-1].decision_id is not None, "decision_id must be initialized"

    def test_session_guard_event_has_turn_id(
        self, guard: SessionGuard, telemetry: CognitiveTelemetry
    ) -> None:
        guard.create_session("claude-haiku-4.5", {}, turn_id="turn-99")
        events = telemetry.query(event_type="session_guard")
        assert events[-1].turn_id == "turn-99", "turn_id is not valid"

    def test_session_guard_event_payload_stripped_params(
        self, guard: SessionGuard, telemetry: CognitiveTelemetry
    ) -> None:
        guard.create_session("claude-haiku-4.5", {"reasoning_effort": "high"})
        events = telemetry.query(event_type="session_guard")
        payload = events[-1].payload
        assert "reasoning_effort" in payload["stripped_params"], "Condition must be true"

    def test_no_telemetry_guard_still_works(self) -> None:
        """Guard without telemetry must not raise."""
        guard = SessionGuard(telemetry=None)
        result = guard.create_session("claude-haiku-4.5", {"reasoning_effort": "low"})
        assert result.safe_config is not None, "safe_config must be initialized"


# ---------------------------------------------------------------------------
# Convenience wrappers
# ---------------------------------------------------------------------------


class TestSafeCreateSession:
    def setup_method(self) -> None:
        reset_default_guard()

    def teardown_method(self) -> None:
        reset_default_guard()

    def test_safe_create_session_returns_result(self) -> None:
        result = safe_create_session("claude-haiku-4.5", {"max_tokens": 512})
        assert isinstance(result, SessionCreateResult)

    def test_safe_create_session_strips_reasoning_effort_from_haiku(self) -> None:
        result = safe_create_session(
            "claude-haiku-4.5",
            {"reasoning_effort": "high", "max_tokens": 2048},
        )
        assert "reasoning_effort" not in result.safe_config, "Result must not be empty"

    def test_get_default_guard_singleton(self) -> None:
        g1 = get_default_guard()
        g2 = get_default_guard()
        assert g1 is g2, "g1 is not valid"

    def test_reset_default_guard_clears_singleton(self) -> None:
        g1 = get_default_guard()
        reset_default_guard()
        g2 = get_default_guard()
        assert g1 is not g2, "g1 is not valid"
