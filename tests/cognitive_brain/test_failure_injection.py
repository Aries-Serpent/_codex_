"""Failure-injection tests for the Cognitive Brain runtime.

Covers the regression modes called out in the problem statement:

A) Unsupported reasoning param error class — must be impossible by construction.
B) Negotiator interception — every session.create path must pass through it.
C) Kernel auto-load missing — assert_loaded must trigger boot or raise.
D) Shell policy bypass — policy-gated commands must be checked.
E) Model capability outage simulation — stale / empty registry safe-fallback.
F) Stale capability cache — invalidation triggers re-build.
"""

from __future__ import annotations

import pytest

from src.codex.cognitive_brain.capability_registry import (
    CapabilityRegistry,
    ModelCapabilityProfile,
)
from src.codex.cognitive_brain.kernel import (
    CognitiveBrainKernel,
    KernelConfig,
    reset_kernel,
)
from src.codex.cognitive_brain.model_negotiator import ModelNegotiator
from src.codex.cognitive_brain.session_guard import SessionGuard
from src.codex.cognitive_brain.shell_policy import PolicyVerdict, ShellPolicy

# ---------------------------------------------------------------------------
# A) Unsupported reasoning param — impossible by construction
# ---------------------------------------------------------------------------


class TestReasoningParamImpossibleByConstruction:
    """FR regression: unsupported reasoning_effort errors must be prevented."""

    _LIGHTWEIGHT_MODELS = [
        "claude-haiku-4.5",
        "gpt-5-mini",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "mai-code-1-flash-picker",
    ]

    @pytest.mark.parametrize("model_id", _LIGHTWEIGHT_MODELS)
    def test_lightweight_model_cannot_receive_reasoning_effort(self, model_id: str) -> None:
        """For every lightweight model, reasoning_effort must be stripped."""
        guard = SessionGuard()
        result = guard.create_session(
            model_id,
            {"reasoning_effort": "high", "max_tokens": 1024},
        )
        assert (
            "reasoning_effort" not in result.safe_config
        ), f"Model {model_id!r} must not receive reasoning_effort in safe_config"

    @pytest.mark.parametrize("model_id", _LIGHTWEIGHT_MODELS)
    def test_lightweight_model_cannot_receive_thinking(self, model_id: str) -> None:
        guard = SessionGuard()
        result = guard.create_session(
            model_id,
            {"thinking": {"type": "enabled"}, "max_tokens": 1024},
        )
        assert (
            "thinking" not in result.safe_config
        ), f"Model {model_id!r} must not receive 'thinking' in safe_config"


# ---------------------------------------------------------------------------
# B) Negotiator interception — every create path
# ---------------------------------------------------------------------------


class TestNegotiatorInterception:
    """Ensure no session config bypasses the negotiator."""

    def test_session_guard_always_calls_negotiator(self) -> None:
        """SessionGuard must always negotiate — verify stripped_params populated."""
        guard = SessionGuard()
        # haiku + reasoning_effort → negotiator must strip it.
        result = guard.create_session(
            "claude-haiku-4.5",
            {"reasoning_effort": "medium"},
        )
        # If negotiator was bypassed, stripped_params would be empty.
        assert "reasoning_effort" in result.params_stripped

    def test_negotiation_result_model_key_always_set(self) -> None:
        guard = SessionGuard()
        for model in ["claude-haiku-4.5", "claude-sonnet-5", "gpt-5-mini"]:
            result = guard.create_session(model, {"max_tokens": 512})
            assert (
                "model" in result.safe_config
            ), f"'model' key missing from safe_config for {model!r}"

    def test_model_negotiator_strips_on_direct_call(self) -> None:
        negotiator = ModelNegotiator()
        negotiation = negotiator.negotiate(
            "claude-haiku-4.5",
            {"reasoning_effort": "low", "max_tokens": 2048},
        )
        assert "reasoning_effort" not in negotiation.safe_config


# ---------------------------------------------------------------------------
# C) Kernel auto-load guard
# ---------------------------------------------------------------------------


class TestKernelAutoLoadGuard:
    def setup_method(self) -> None:
        reset_kernel()

    def teardown_method(self) -> None:
        reset_kernel()

    def test_assert_loaded_auto_boots_when_not_loaded(self) -> None:
        """assert_loaded must auto-boot the kernel (default: failsafe=off)."""
        k = CognitiveBrainKernel(config=KernelConfig())
        assert not k.is_loaded
        k.assert_loaded()
        assert k.is_loaded

    def test_assert_loaded_on_already_booted_kernel(self) -> None:
        k = CognitiveBrainKernel(config=KernelConfig())
        k.boot()
        k.assert_loaded()  # must not raise
        assert k.is_loaded

    def test_assert_loaded_raises_when_failsafe_off(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With COGNITIVE_BRAIN_FAILSAFE_OFF=true, assert_loaded must raise."""
        monkeypatch.setenv("COGNITIVE_BRAIN_FAILSAFE_OFF", "true")
        k = CognitiveBrainKernel(config=KernelConfig())
        assert not k.is_loaded
        with pytest.raises(RuntimeError, match="assert_loaded"):
            k.assert_loaded()

    def test_auto_load_respects_failsafe_off(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """COGNITIVE_BRAIN_FAILSAFE_OFF=true disables auto_load (returns None)."""
        monkeypatch.setenv("COGNITIVE_BRAIN_FAILSAFE_OFF", "true")
        from src.codex.cognitive_brain.kernel import auto_load

        result = auto_load()
        assert result is None

    def test_auto_load_disabled_by_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("COGNITIVE_BRAIN_AUTO_LOAD", "false")
        from src.codex.cognitive_brain.kernel import auto_load

        result = auto_load()
        assert result is None


# ---------------------------------------------------------------------------
# D) Shell policy bypass prevention
# ---------------------------------------------------------------------------


class TestShellPolicyBypass:
    def test_deny_by_default_blocks_unknown_commands(self) -> None:
        """Shell policy must deny unknown commands by default."""
        policy = ShellPolicy(default_shell_enabled=False)
        decision = policy.gate("evil_command --exploit")
        assert decision.verdict == PolicyVerdict.DENY

    def test_deny_always_overrides_allow_for_dangerous_commands(self) -> None:
        policy = ShellPolicy()
        # sudo is in deny patterns — must not be allowed even if someone adds
        # "sudo *" to the allow list.
        decision = policy.gate("sudo apt-get update")
        assert decision.verdict == PolicyVerdict.DENY

    def test_cwd_allowlist_prevents_traversal(self) -> None:
        policy = ShellPolicy(working_dir_allowlist=["/repo"])
        decision = policy.gate("cat /etc/passwd", cwd="/etc")
        assert decision.verdict == PolicyVerdict.DENY

    def test_kernel_allow_shell_false_means_no_shell_in_plan(self) -> None:
        """Kernel with allow_shell=False must not select shell as primary tool."""
        k = CognitiveBrainKernel(config=KernelConfig(allow_shell=False))
        k.boot()
        plan = k.plan_tools("local_build")
        # Shell must not be the primary tool when allow_shell=False.
        assert plan.primary_tool != "shell"


# ---------------------------------------------------------------------------
# E) Model capability outage — empty registry safe-fallback
# ---------------------------------------------------------------------------


class TestModelCapabilityOutage:
    def test_negotiator_handles_unknown_model_gracefully(self) -> None:
        """Unknown model → default safe profile; must not raise."""
        negotiator = ModelNegotiator()
        result = negotiator.negotiate(
            "totally-unknown-model-xyz",
            {"reasoning_effort": "high", "max_tokens": 1024},
        )
        # Should strip reasoning_effort (unknown model → no reasoning support)
        # OR keep it (model unknown → safe defaults apply). Either way: no raise.
        assert isinstance(result.safe_config, dict)

    def test_negotiator_with_empty_fallback_chain_returns_stripped_config(
        self,
    ) -> None:
        """Empty fallback chain + unmet requirements → fallback_used=False, no crash."""
        negotiator = ModelNegotiator(fallback_chain=[])
        result = negotiator.negotiate(
            "claude-haiku-4.5",
            {"reasoning_effort": "high"},
            required_capabilities=["reasoning_effort"],
        )
        # Can't find a fallback, but must not raise.
        assert result.fallback_used is False
        assert "reasoning_effort" not in result.safe_config

    def test_registry_with_injected_no_reasoning_profile(self) -> None:
        """Injected profile overrides built-in; negotiator must use override."""
        registry = CapabilityRegistry()
        custom_profile = ModelCapabilityProfile(
            model_id="custom-model-v1",
            supports_reasoning_effort=False,
        )
        registry.register(custom_profile)
        negotiator = ModelNegotiator(registry=registry)
        result = negotiator.negotiate(
            "custom-model-v1",
            {"reasoning_effort": "low"},
        )
        assert "reasoning_effort" not in result.safe_config


# ---------------------------------------------------------------------------
# F) Stale capability cache
# ---------------------------------------------------------------------------


class TestStaleCapabilityCache:
    def test_invalidate_all_forces_rebuild(self) -> None:
        registry = CapabilityRegistry(ttl_seconds=3600)
        registry.get("claude-haiku-4.5")
        assert len(registry.all_known()) == 1
        registry.invalidate()
        assert len(registry.all_known()) == 0

    def test_invalidate_single_model_clears_only_that(self) -> None:
        registry = CapabilityRegistry(ttl_seconds=3600)
        registry.get("claude-haiku-4.5")
        registry.get("claude-sonnet-5")
        registry.invalidate("claude-haiku-4.5")
        known = registry.all_known()
        assert "claude-haiku-4.5" not in known
        assert "claude-sonnet-5" in known

    def test_expired_cache_rebuilds_on_get(self) -> None:
        """TTL=0 means every get rebuilds the profile."""
        registry = CapabilityRegistry(ttl_seconds=0)
        p1 = registry.get("claude-haiku-4.5")
        p2 = registry.get("claude-haiku-4.5")
        # Both must be valid profiles even though cache always expires.
        assert p1.model_id == "claude-haiku-4.5"
        assert p2.model_id == "claude-haiku-4.5"

    def test_register_overrides_ttl(self) -> None:
        """Injected profile must persist through the normal TTL window."""
        registry = CapabilityRegistry(ttl_seconds=3600)
        override = ModelCapabilityProfile(
            model_id="new-model-v2",
            supports_reasoning_effort=True,
        )
        registry.register(override)
        profile = registry.get("new-model-v2")
        assert profile.supports_reasoning_effort is True
