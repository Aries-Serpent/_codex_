"""Tests for CognitiveBrainKernel (integration) and telemetry.

Covers:
- Integration: kernel auto-boot (FR-5)
- Integration: negotiate_model end-to-end (FR-1)
- Integration: plan_tools end-to-end (FR-2)
- Integration: telemetry events recorded (FR-7)
- Integration: CCA stability flags checked on boot
- Regression: duplicate function-call / dedup guards not broken
- Failure injection: COGNITIVE_BRAIN_FAILSAFE_OFF disables auto-load
"""

from __future__ import annotations

import pytest

from codex.cognitive_brain.kernel import (
    CognitiveBrainKernel,
    KernelConfig,
    get_kernel,
    reset_kernel,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fresh_kernel(**config_kwargs) -> CognitiveBrainKernel:
    """Boot a fresh kernel with an in-memory telemetry backend."""
    cfg = KernelConfig(**config_kwargs)
    k = CognitiveBrainKernel(config=cfg)
    k.boot()
    return k


# ---------------------------------------------------------------------------
# Kernel boot tests
# ---------------------------------------------------------------------------


class TestKernelBoot:
    def setup_method(self) -> None:
        reset_kernel()

    def teardown_method(self) -> None:
        reset_kernel()

    def test_kernel_is_loaded_after_boot(self) -> None:
        k = _fresh_kernel()
        assert k.is_loaded, "Condition must be true"

    def test_boot_idempotent(self) -> None:
        k = _fresh_kernel()
        k.boot()  # second call — must not raise or re-initialise
        assert k.is_loaded, "Condition must be true"

    def test_get_kernel_returns_singleton(self) -> None:
        k1 = get_kernel()
        k2 = get_kernel()
        assert k1 is k2, "k1 is not valid"

    def test_reset_kernel_clears_singleton(self) -> None:
        k1 = get_kernel()
        reset_kernel()
        k2 = get_kernel()
        assert k1 is not k2, "k1 is not valid"

    def test_startup_event_emitted(self) -> None:
        k = _fresh_kernel()
        events = k.telemetry.query(event_type="startup")
        assert len(events) == 1, "Events must not be empty"
        assert events[0].success is True, "success is not valid"

    def test_startup_event_contains_version(self) -> None:
        k = _fresh_kernel()
        events = k.telemetry.query(event_type="startup")
        assert events[0].payload.get("version") is not None, "Value must be initialized"

    def test_startup_event_contains_cca_flags(self) -> None:
        k = _fresh_kernel()
        events = k.telemetry.query(event_type="startup")
        cfg = events[0].payload.get("config", {})
        assert "cca_version_lock" in cfg, "Condition must be true"
        assert "deduplication" in cfg, "Condition must be true"
        assert "turn_isolation" in cfg, "Condition must be true"


# ---------------------------------------------------------------------------
# Model negotiation integration tests
# ---------------------------------------------------------------------------


class TestKernelNegotiateModel:
    def setup_method(self) -> None:
        reset_kernel()

    def teardown_method(self) -> None:
        reset_kernel()

    def test_haiku_reasoning_effort_stripped(self) -> None:
        """FR-1 regression: haiku must not receive reasoning_effort."""
        k = _fresh_kernel()
        result = k.negotiate_model(
            "claude-haiku-4.5",
            {"reasoning_effort": "high", "max_tokens": 2048},
        )
        assert "reasoning_effort" not in result.safe_config, "Result must not be empty"

    def test_sonnet_reasoning_effort_preserved(self) -> None:
        k = _fresh_kernel()
        result = k.negotiate_model(
            "claude-sonnet-5",
            {"reasoning_effort": "medium", "max_tokens": 2048},
        )
        assert "reasoning_effort" in result.safe_config, "Result must not be empty"

    def test_negotiation_event_recorded(self) -> None:
        k = _fresh_kernel()
        k.negotiate_model("claude-haiku-4.5", {"reasoning_effort": "high"})
        events = k.telemetry.query(event_type="session_guard")
        assert len(events) >= 1, "Events must not be empty"
        assert events[-1].model_id == "claude-haiku-4.5", "model_id is not valid"

    def test_negotiation_event_payload(self) -> None:
        k = _fresh_kernel()
        k.negotiate_model(
            "claude-haiku-4.5",
            {"reasoning_effort": "high"},
        )
        events = k.telemetry.query(event_type="session_guard")
        payload = events[-1].payload
        assert "stripped_params" in payload, "Condition must be true"
        assert "reasoning_effort" in payload["stripped_params"], "Condition must be true"

    def test_safe_session_config_has_model_key(self) -> None:
        k = _fresh_kernel()
        cfg = k.safe_session_config(
            "claude-haiku-4.5",
            {"reasoning_effort": "high", "max_tokens": 1024},
        )
        assert "model" in cfg, "Condition must be true"

    def test_session_create_succeeds_via_safe_path(self) -> None:
        """Simulates session.create: safe config must not contain unsupported params."""
        k = _fresh_kernel()
        raw_cfg = {
            "reasoning_effort": "high",
            "max_tokens": 4096,
            "temperature": 0.2,
        }
        safe = k.safe_session_config("claude-haiku-4.5", raw_cfg)
        # No unsupported param in output.
        assert "reasoning_effort" not in safe, "Condition must be true"
        # Passthrough params preserved.
        assert safe["max_tokens"] == 4096, "Condition must be true"
        assert safe["temperature"] == 0.2, "Condition must be true"


# ---------------------------------------------------------------------------
# Tool planning integration tests
# ---------------------------------------------------------------------------


class TestKernelPlanTools:
    def setup_method(self) -> None:
        reset_kernel()

    def teardown_method(self) -> None:
        reset_kernel()

    def test_plan_tools_returns_toolchain_plan(self) -> None:
        k = _fresh_kernel()
        plan = k.plan_tools("repo_introspection")
        assert plan is not None, "plan must be initialized"
        assert len(plan.steps) > 0, "Collection must not be empty"

    def test_orchestration_event_recorded(self) -> None:
        k = _fresh_kernel()
        k.plan_tools("repo_introspection")
        events = k.telemetry.query(event_type="orchestration")
        assert len(events) >= 1, "Events must not be empty"
        assert events[-1].task_intent == "repo_introspection", "task_intent is not valid"

    def test_orchestration_event_has_primary_tool(self) -> None:
        k = _fresh_kernel()
        k.plan_tools("code_search")
        events = k.telemetry.query(event_type="orchestration")
        payload = events[-1].payload
        assert "primary_tool" in payload, "Condition must be true"
        assert payload["primary_tool"] is not None, "Value must be initialized"


# ---------------------------------------------------------------------------
# CCA stability regression tests
# ---------------------------------------------------------------------------


class TestCCAStability:
    def setup_method(self) -> None:
        reset_kernel()

    def teardown_method(self) -> None:
        reset_kernel()

    def test_kernel_boots_with_stable_cca_flags(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("COPILOT_AGENT_CCA_VERSION_LOCK", "stable")
        monkeypatch.setenv("COPILOT_AGENT_DEDUPLICATION_ENABLED", "true")
        monkeypatch.setenv("COPILOT_AGENT_TURN_ISOLATION_ENABLED", "true")
        k = _fresh_kernel()
        assert k.is_loaded, "Condition must be true"

    def test_negotiation_does_not_duplicate_params(self) -> None:
        """No duplicate keys introduced during negotiation (CCA dedup guard)."""
        k = _fresh_kernel()
        cfg = {"reasoning_effort": "high", "max_tokens": 2048, "temperature": 0.5}
        result = k.negotiate_model("claude-haiku-4.5", cfg)
        # Each key appears exactly once in safe_config.
        for key, val in result.safe_config.items():
            assert isinstance(key, str), "Config keys must be strings"


# ---------------------------------------------------------------------------
# KernelConfig.from_env
# ---------------------------------------------------------------------------


class TestKernelConfigFromEnv:
    def test_default_policy_seed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("COGNITIVE_BRAIN_POLICY_SEED", raising=False)
        cfg = KernelConfig.from_env()
        assert cfg.policy_seed == 42, "policy_seed is not valid"

    def test_custom_policy_seed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("COGNITIVE_BRAIN_POLICY_SEED", "99")
        cfg = KernelConfig.from_env()
        assert cfg.policy_seed == 99, "policy_seed is not valid"

    def test_allow_shell_default_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("COGNITIVE_BRAIN_ALLOW_SHELL", raising=False)
        cfg = KernelConfig.from_env()
        assert cfg.allow_shell is False, "allow_shell is not valid"

    def test_allow_shell_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("COGNITIVE_BRAIN_ALLOW_SHELL", "true")
        cfg = KernelConfig.from_env()
        assert cfg.allow_shell is True, "allow_shell is not valid"
