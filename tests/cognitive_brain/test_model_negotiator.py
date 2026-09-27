"""Tests for ModelNegotiator and CapabilityRegistry.

Covers:
- Unit: unsupported param stripping (claude-haiku-4.5 regression)
- Unit: fallback model selection
- Unit: capability profile cache TTL
- Integration: session config safe-path
- Failure injection: model list unavailable → safe defaults
"""

from __future__ import annotations

import pytest

from codex.cognitive_brain.capability_registry import (
    CapabilityRegistry,
    ModelCapabilityProfile,
)
from codex.cognitive_brain.fallbacks import safe_default_config
from codex.cognitive_brain.model_negotiator import ModelNegotiator

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def registry() -> CapabilityRegistry:
    """Fresh registry for each test."""
    return CapabilityRegistry(ttl_seconds=3600)


@pytest.fixture()
def negotiator(registry: CapabilityRegistry) -> ModelNegotiator:
    return ModelNegotiator(registry=registry)


# ---------------------------------------------------------------------------
# CapabilityRegistry unit tests
# ---------------------------------------------------------------------------


class TestCapabilityRegistry:
    def test_haiku_does_not_support_reasoning_effort(self, registry: CapabilityRegistry) -> None:
        """claude-haiku-4.5 must NOT have reasoning_effort capability."""
        profile = registry.get("claude-haiku-4.5")
        assert not profile.supports_reasoning_effort, (
            "claude-haiku-4.5 must NOT support reasoning_effort"
        )

    def test_sonnet_supports_reasoning_effort(self, registry: CapabilityRegistry) -> None:
        profile = registry.get("claude-sonnet-5")
        assert profile.supports_reasoning_effort, "Condition must be true"

    def test_opus_supports_reasoning_effort(self, registry: CapabilityRegistry) -> None:
        profile = registry.get("claude-opus-4.8")
        assert profile.supports_reasoning_effort, "Condition must be true"

    def test_unknown_model_gets_default_profile(self, registry: CapabilityRegistry) -> None:
        profile = registry.get("totally-unknown-model-xyz")
        assert isinstance(profile, ModelCapabilityProfile)
        assert profile.model_id == "totally-unknown-model-xyz", "model_id is not valid"
        # Unknown models default to no reasoning_effort.
        assert not profile.supports_reasoning_effort, "Condition must be true"

    def test_register_overrides_builtin(self, registry: CapabilityRegistry) -> None:
        custom = ModelCapabilityProfile(
            model_id="my-custom-model",
            supports_reasoning_effort=True,
        )
        registry.register(custom)
        fetched = registry.get("my-custom-model")
        assert fetched.supports_reasoning_effort, "Condition must be true"

    def test_cache_hit_returns_same_profile(self, registry: CapabilityRegistry) -> None:
        first = registry.get("claude-haiku-4.5")
        second = registry.get("claude-haiku-4.5")
        assert first is second, "first is not valid"

    def test_invalidate_clears_entry(self, registry: CapabilityRegistry) -> None:
        registry.get("claude-haiku-4.5")
        registry.invalidate("claude-haiku-4.5")
        assert "claude-haiku-4.5" not in registry.all_known(), "Condition must be true"

    def test_invalidate_all(self, registry: CapabilityRegistry) -> None:
        registry.get("claude-haiku-4.5")
        registry.get("claude-sonnet-5")
        registry.invalidate()
        assert registry.all_known() == {}, "Condition must be true"

    def test_supports_helper_reasoning_effort(self, registry: CapabilityRegistry) -> None:
        haiku = registry.get("claude-haiku-4.5")
        assert not haiku.supports("reasoning_effort"), "Condition must be true"
        sonnet = registry.get("claude-sonnet-5")
        assert sonnet.supports("reasoning_effort"), "Condition must be true"

    def test_supports_helper_streaming_default(self, registry: CapabilityRegistry) -> None:
        profile = registry.get("claude-haiku-4.5")
        assert profile.supports("streaming"), "Condition must be true"

    def test_supports_unknown_capability_returns_false(self, registry: CapabilityRegistry) -> None:
        profile = registry.get("claude-haiku-4.5")
        assert not profile.supports("future_capability_xyz"), "Condition must be true"


# ---------------------------------------------------------------------------
# ModelNegotiator unit tests
# ---------------------------------------------------------------------------


class TestModelNegotiator:
    def test_strips_reasoning_effort_from_haiku(self, negotiator: ModelNegotiator) -> None:
        """Core regression: reasoning_effort must be stripped for claude-haiku-4.5."""
        config = {"reasoning_effort": "high", "max_tokens": 2048}
        result = negotiator.negotiate("claude-haiku-4.5", config)
        assert "reasoning_effort" not in result.safe_config, (
            "reasoning_effort must be stripped for claude-haiku-4.5"
        )
        assert "reasoning_effort" in result.stripped_params, "Result must not be empty"

    def test_preserves_reasoning_effort_on_sonnet(self, negotiator: ModelNegotiator) -> None:
        config = {"reasoning_effort": "high", "max_tokens": 2048}
        result = negotiator.negotiate("claude-sonnet-5", config)
        assert "reasoning_effort" in result.safe_config, "Result must not be empty"
        assert result.stripped_params == [], "Result must not be empty"

    def test_preserves_unrelated_params(self, negotiator: ModelNegotiator) -> None:
        config = {"reasoning_effort": "low", "max_tokens": 4096, "temperature": 0.5}
        result = negotiator.negotiate("claude-haiku-4.5", config)
        assert result.safe_config["max_tokens"] == 4096, "Result must not be empty"
        assert result.safe_config["temperature"] == 0.5, "Result must not be empty"

    def test_fallback_selected_when_required_cap_missing(
        self, negotiator: ModelNegotiator
    ) -> None:
        config = {"max_tokens": 2048}
        result = negotiator.negotiate(
            "claude-haiku-4.5",
            config,
            required_capabilities=["reasoning_effort"],
        )
        assert result.fallback_used, "Fallback should be selected for required reasoning_effort"
        assert result.resolved_model_id != "claude-haiku-4.5", "Result must not be empty"
        assert result.resolved_model_id in negotiator._fallback_chain, "Result must not be empty"

    def test_no_fallback_needed_when_cap_met(self, negotiator: ModelNegotiator) -> None:
        config = {"reasoning_effort": "medium"}
        result = negotiator.negotiate(
            "claude-sonnet-5",
            config,
            required_capabilities=["reasoning_effort"],
        )
        assert not result.fallback_used, "Result must not be empty"
        assert result.resolved_model_id == "claude-sonnet-5", "Result must not be empty"

    def test_model_changed_property(self, negotiator: ModelNegotiator) -> None:
        config = {"max_tokens": 1024}
        result = negotiator.negotiate(
            "claude-haiku-4.5",
            config,
            required_capabilities=["reasoning_effort"],
        )
        assert result.model_changed, "Result must not be empty"

    def test_no_params_to_strip_returns_unchanged_config(
        self, negotiator: ModelNegotiator
    ) -> None:
        config = {"max_tokens": 512}
        result = negotiator.negotiate("claude-haiku-4.5", config)
        assert result.safe_config == {"max_tokens": 512}, "Result must not be empty"
        assert result.stripped_params == [], "Result must not be empty"
        assert not result.fallback_used, "Result must not be empty"

    def test_safe_session_config_injects_model_key(self, negotiator: ModelNegotiator) -> None:
        config = {"reasoning_effort": "high", "max_tokens": 1024}
        # Without required_capabilities, param is stripped but no fallback is selected.
        out = negotiator.safe_session_config("claude-haiku-4.5", config)
        assert "model" in out, "Condition must be true"
        assert "reasoning_effort" not in out, "Condition must be true"

    def test_original_config_not_mutated(self, negotiator: ModelNegotiator) -> None:
        original = {"reasoning_effort": "high", "max_tokens": 2048}
        backup = dict(original)
        negotiator.negotiate("claude-haiku-4.5", original)
        assert original == backup, "negotiate() must not mutate the input dict"

    def test_empty_config_succeeds(self, negotiator: ModelNegotiator) -> None:
        result = negotiator.negotiate("claude-haiku-4.5", {})
        assert result.safe_config == {}, "Result must not be empty"
        assert result.stripped_params == [], "Result must not be empty"

    def test_custom_fallback_chain(self, registry: CapabilityRegistry) -> None:
        custom_chain = ["claude-sonnet-4.6", "claude-opus-4.7"]
        neg = ModelNegotiator(registry=registry, fallback_chain=custom_chain)
        result = neg.negotiate(
            "claude-haiku-4.5",
            {"max_tokens": 512},
            required_capabilities=["reasoning_effort"],
        )
        assert result.resolved_model_id in custom_chain, "Result must not be empty"

    def test_exhausted_fallback_chain_returns_original(
        self, registry: CapabilityRegistry
    ) -> None:
        """When no fallback satisfies requirements, proceed with original model."""
        # Register only a dummy model that also lacks the capability.
        dummy = ModelCapabilityProfile(model_id="dummy-weak", supports_reasoning_effort=False)
        registry.register(dummy)
        neg = ModelNegotiator(registry=registry, fallback_chain=["dummy-weak"])
        result = neg.negotiate(
            "claude-haiku-4.5",
            {"max_tokens": 512},
            required_capabilities=["reasoning_effort"],
        )
        # No capable fallback found → original model retained, no crash.
        assert result.resolved_model_id == "claude-haiku-4.5", "Result must not be empty"
        assert not result.fallback_used, "Result must not be empty"

    def test_thinking_param_stripped_for_haiku(self, negotiator: ModelNegotiator) -> None:
        """'thinking' is an Anthropic alias for extended reasoning; also gated."""
        config = {"thinking": {"type": "enabled", "budget_tokens": 5000}, "max_tokens": 2048}
        result = negotiator.negotiate("claude-haiku-4.5", config)
        assert "thinking" not in result.safe_config, "Result must not be empty"
        assert "thinking" in result.stripped_params, "Result must not be empty"


# ---------------------------------------------------------------------------
# Safe-default fallback
# ---------------------------------------------------------------------------


class TestSafeDefaultConfig:
    def test_returns_dict_with_model_key(self) -> None:
        cfg = safe_default_config()
        assert "model" in cfg, "Condition must be true"
        assert isinstance(cfg["model"], str)

    def test_no_reasoning_effort_in_defaults(self) -> None:
        cfg = safe_default_config()
        assert "reasoning_effort" not in cfg, "Condition must be true"

    def test_custom_model_id(self) -> None:
        cfg = safe_default_config("claude-opus-4.8")
        assert cfg["model"] == "claude-opus-4.8", "Condition must be true"
