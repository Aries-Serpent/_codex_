"""
Comprehensive tests for src/codex_ml/safety/moderation.py

This module provides exhaustive testing of the moderation system,
including offline filtering, provider integration, and policy enforcement.

Test Coverage: 30+ tests targeting 70%+ coverage
Phase: 3.2 - Safety Module Testing
"""

from __future__ import annotations

import tempfile
from unittest.mock import MagicMock, patch

import pytest

try:
    from codex_ml.safety.moderation import (
        ModerationAdapter,
        ModerationDecision,
        ModerationRejection,
        ModerationSettings,
    )

    MODERATION_AVAILABLE = True
except ImportError:
    MODERATION_AVAILABLE = False


pytestmark = pytest.mark.skipif(
    not MODERATION_AVAILABLE, reason="codex_ml.safety.moderation not available"
)


# =============================================================================
# Advanced ModerationSettings Tests
# =============================================================================


class TestModerationSettingsAdvanced:
    """Advanced tests for ModerationSettings."""

    def test_settings_all_combinations(self):
        """Test all possible settings combinations."""
        combos = [
            {"enabled": False, "fail_open": False},
            {"enabled": True, "fail_open": False},
            {"enabled": True, "fail_open": True},
        ]

        for combo in combos:
            settings = ModerationSettings(**combo)
            assert settings.enabled == combo["enabled"], "enabled is not valid"
            assert settings.fail_open == combo["fail_open"], "fail_open is not valid"

    def test_settings_with_custom_paths(self):
        """Test settings with custom file paths."""
        settings = ModerationSettings(
            enabled=True,
            rules_path="/custom/rules.yaml",
            audit_log="/var/log/moderation/audit.jsonl",
        )

        assert settings.rules_path == "/custom/rules.yaml", "rules_path is not valid"
        assert settings.audit_log == "/var/log/moderation/audit.jsonl", "audit_log is not valid"

    def test_settings_provider_variants(self):
        """Test different provider configurations."""
        providers = [
            "offline",
            "openai",
            "custom.module:function",
            "",
        ]

        for provider in providers:
            settings = ModerationSettings(provider=provider)
            assert settings.provider == provider, "provider is not valid"

    def test_settings_label_for_tracking(self):
        """Test label field for environment tracking."""
        labels = ["production", "staging", "dev", "test-suite"]

        for label in labels:
            settings = ModerationSettings(label=label)
            assert settings.label == label, "label is not valid"

    def test_settings_immutability(self):
        """Test that settings can be safely passed around."""
        settings = ModerationSettings(enabled=True)

        # Create adapter with settings
        ModerationAdapter(settings)

        # Original settings should be unchanged
        assert settings.enabled is True, "enabled is not valid"


# =============================================================================
# Advanced ModerationDecision Tests
# =============================================================================


class TestModerationDecisionAdvanced:
    """Advanced tests for ModerationDecision."""

    def test_decision_with_complex_details(self):
        """Test decision with complex details dict."""
        details = {
            "scores": {"toxicity": 0.1, "hate": 0.05},
            "categories": ["safe", "neutral"],
            "confidence": 0.95,
            "metadata": {"model": "v1", "timestamp": "2024-01-15"},
        }

        decision = ModerationDecision(
            approved=True,
            stage="preflight",
            provider="custom",
            details=details,
        )

        assert decision.details["scores"]["toxicity"] == 0.1, "Condition must be true"
        assert decision.details["metadata"]["model"] == "v1", "Data must not be empty"

    def test_decision_to_dict_comprehensive(self):
        """Test comprehensive to_dict conversion."""
        decision = ModerationDecision(
            approved=False,
            stage="postflight",
            provider="openai",
            reasons=("violence", "hate_speech", "self_harm"),
            matches=("pattern1", "pattern2"),
            sanitized_text="[REDACTED] safe content",
            details={"score": 0.85, "threshold": 0.5},
        )

        result = decision.to_dict()

        assert result["approved"] is False, "Result must not be empty"
        assert result["stage"] == "postflight", "Result must not be empty"
        assert result["provider"] == "openai", "Result must not be empty"
        assert len(result["reasons"]) == 3, "Collection must not be empty"
        assert len(result["matches"]) == 2, "Collection must not be empty"
        assert result["sanitized_text"] == "[REDACTED] safe content", "Result must not be empty"
        assert result["details"]["score"] == 0.85, "Result must not be empty"

    def test_decision_equality_via_dict(self):
        """Test decision equality through dict comparison."""
        decision1 = ModerationDecision(
            approved=True,
            stage="preflight",
            provider="offline",
            reasons=("safe",),
        )

        dict1 = decision1.to_dict()

        decision2 = ModerationDecision(
            approved=dict1["approved"],
            stage=dict1["stage"],
            provider=dict1["provider"],
            reasons=tuple(dict1["reasons"]),
        )

        dict2 = decision2.to_dict()

        # Compare important fields
        assert dict1["approved"] == dict2["approved"], "Condition must be true"
        assert dict1["stage"] == dict2["stage"], "Condition must be true"
        assert dict1["provider"] == dict2["provider"], "Condition must be true"

    def test_decision_with_empty_collections(self):
        """Test decision with empty reasons and matches."""
        decision = ModerationDecision(
            approved=True,
            stage="preflight",
            provider="offline",
            reasons=(),
            matches=(),
        )

        result = decision.to_dict()
        assert result["reasons"] == [], "Result must not be empty"
        assert result["matches"] == [], "Result must not be empty"

    def test_decision_sanitized_text_none(self):
        """Test decision with None sanitized_text."""
        decision = ModerationDecision(
            approved=True,
            stage="preflight",
            provider="offline",
            sanitized_text=None,
        )

        assert decision.sanitized_text is None, "sanitized_text is not valid"
        result = decision.to_dict()
        assert result["sanitized_text"] is None, "Result must not be empty"


# =============================================================================
# Advanced ModerationRejection Tests
# =============================================================================


class TestModerationRejectionAdvanced:
    """Advanced tests for ModerationRejection."""

    def test_rejection_error_message_content(self):
        """Test that rejection message contains useful info."""
        decision = ModerationDecision(
            approved=False,
            stage="preflight",
            provider="offline",
            matches=("harmful_pattern", "toxic_content"),
        )

        rejection = ModerationRejection("preflight", decision)
        error_msg = str(rejection)

        assert "preflight" in error_msg, "Error should be raised or set"
        assert "harmful_pattern" in error_msg or "toxic_content" in error_msg, "Content must not be empty"

    def test_rejection_with_multiple_reasons(self):
        """Test rejection with multiple reasons."""
        decision = ModerationDecision(
            approved=False,
            stage="postflight",
            provider="openai",
            reasons=("violence", "hate", "harassment"),
        )

        rejection = ModerationRejection("postflight", decision)
        error_msg = str(rejection)

        # Should mention at least one reason
        assert any(r in error_msg for r in ["violence", "hate", "harassment"])

    def test_rejection_preserves_provider_error(self):
        """Test that provider errors are preserved."""
        decision = ModerationDecision(
            approved=False,
            stage="preflight",
            provider="external",
        )

        provider_error = Exception("API timeout after 30s")
        rejection = ModerationRejection(
            "preflight",
            decision,
            provider_error=provider_error,
        )

        assert rejection.provider_error == provider_error, "Error should be raised or set"
        assert str(rejection.provider_error) == "API timeout after 30s", "Error should be raised or set"

    def test_rejection_can_be_caught(self):
        """Test that rejection can be caught as exception."""
        decision = ModerationDecision(
            approved=False,
            stage="preflight",
            provider="offline",
        )

        def _do_raise(d: object) -> None:
            raise ModerationRejection("preflight", d)  # type: ignore[arg-type]

        with pytest.raises(ModerationRejection) as exc_info:
            _do_raise(decision)

        assert exc_info.value.stage == "preflight", "Value must be initialized"
        assert exc_info.value.decision == decision, "Value must be initialized"

    def test_rejection_inherits_runtime_error(self):
        """Test ModerationRejection is RuntimeError."""
        assert issubclass(ModerationRejection, RuntimeError)

        decision = ModerationDecision(
            approved=False,
            stage="preflight",
            provider="offline",
        )

        rejection = ModerationRejection("preflight", decision)
        assert isinstance(rejection, RuntimeError)


# =============================================================================
# ModerationAdapter Core Tests
# =============================================================================


class TestModerationAdapterCore:
    """Core functionality tests for ModerationAdapter."""

    def test_adapter_with_disabled_moderation(self):
        """Test adapter behavior when moderation disabled."""
        settings = ModerationSettings(enabled=False)
        adapter = ModerationAdapter(settings)

        # Should return approved for anything
        decision = adapter.review("any text", stage="preflight")

        assert decision.approved is True, "approved is not valid"
        assert decision.provider == "disabled", "provider is not valid"

    def test_adapter_from_settings_classmethod(self):
        """Test creating adapter via from_settings classmethod."""
        settings = ModerationSettings(enabled=True)
        adapter = ModerationAdapter.from_settings(settings)

        assert adapter.settings == settings, "settings is not valid"
        assert isinstance(adapter, ModerationAdapter)

    def test_adapter_provider_name_property(self):
        """Test provider_name property."""
        settings = ModerationSettings(provider="custom-provider")
        adapter = ModerationAdapter(settings)

        # Should return provider name
        assert adapter.provider_name in ["custom-provider", "offline"]

    def test_adapter_with_default_policy(self):
        """Test adapter initialization with default policy."""
        settings = ModerationSettings(enabled=True)
        adapter = ModerationAdapter(
            settings,
            default_policy="/path/to/default/policy.yaml",
        )

        assert adapter._default_policy == "/path/to/default/policy.yaml", "_default_policy is not valid"

    @patch("codex_ml.safety.moderation.importlib.import_module")
    def test_adapter_resolve_provider_success(self, mock_import):
        """Test successful provider resolution."""
        mock_module = MagicMock()
        mock_function = MagicMock()
        mock_module.my_function = mock_function
        mock_import.return_value = mock_module

        settings = ModerationSettings(provider="my.module:my_function")
        adapter = ModerationAdapter(settings)

        # Should have resolved provider
        assert adapter._provider is not None, "_provider must be initialized"

    def test_adapter_resolve_provider_offline(self):
        """Test provider resolution for offline mode."""
        settings = ModerationSettings(provider="offline")
        adapter = ModerationAdapter(settings)

        assert adapter._provider is None, "_provider is not valid"
        assert adapter.provider_name == "offline", "provider_name is not valid"

    def test_adapter_resolve_provider_invalid(self):
        """Test handling of invalid provider format."""
        settings = ModerationSettings(provider="invalid-no-colon")
        adapter = ModerationAdapter(settings)

        # Should fall back to offline
        assert adapter._provider is None, "_provider is not valid"


# =============================================================================
# Review and Enforce Tests
# =============================================================================


class TestReviewAndEnforce:
    """Tests for review and enforce methods."""

    def test_review_with_disabled_moderation(self):
        """Test review when moderation is disabled."""
        settings = ModerationSettings(enabled=False)
        adapter = ModerationAdapter(settings)

        decision = adapter.review("dangerous content", stage="preflight")

        assert decision.approved is True, "approved is not valid"
        assert decision.provider == "disabled", "provider is not valid"

    @patch("codex_ml.safety.filters.SafetyFilters")
    def test_review_offline_mode(self, mock_filters):
        """Test review in offline mode."""
        # Mock offline review
        mock_filter_instance = MagicMock()
        mock_filter_instance.evaluate.return_value = MagicMock(
            allowed=True,
            blocking_matches=[],
            bypassed=False,
            sanitized_text="clean text",
        )
        mock_filters.from_policy_file.return_value = mock_filter_instance

        settings = ModerationSettings(enabled=True, provider="offline")
        adapter = ModerationAdapter(settings)

        decision = adapter.review("test text", stage="preflight")

        assert decision.approved is True, "approved is not valid"
        assert decision.provider == "offline", "provider is not valid"

    @patch("codex_ml.safety.moderation.SafetyFilters")
    def test_enforce_with_approval(self, mock_filters):
        """Test enforce when content is approved."""
        mock_filter_instance = MagicMock()
        mock_filter_instance.evaluate.return_value = MagicMock(
            allowed=True,
            blocking_matches=[],
            bypassed=False,
            sanitized_text="safe text",
        )
        mock_filters.from_policy_file.return_value = mock_filter_instance

        settings = ModerationSettings(enabled=True)
        adapter = ModerationAdapter(settings)

        # Should not raise
        decision = adapter.enforce("safe content", stage="preflight")
        assert decision.approved is True, "approved is not valid"

    @patch("codex_ml.safety.moderation.SafetyFilters")
    def test_enforce_with_rejection(self, mock_filters):
        """Test enforce when content is rejected."""
        mock_match = MagicMock()
        mock_match.rule_id = "TOXIC-001"
        mock_match.description = "Toxic content"
        mock_match.severity = "HIGH"

        mock_filter_instance = MagicMock()
        mock_filter_instance.evaluate.return_value = MagicMock(
            allowed=False,
            blocking_matches=[mock_match],
            bypassed=False,
            sanitized_text="toxic text",
        )
        mock_filter_instance.policy_path = None
        mock_filters.from_policy_file.return_value = mock_filter_instance

        settings = ModerationSettings(enabled=True, fail_open=False)
        adapter = ModerationAdapter(settings)

        with pytest.raises(ModerationRejection):
            adapter.enforce("toxic content", stage="preflight")

    @patch("codex_ml.safety.moderation.SafetyFilters")
    def test_enforce_with_fail_open(self, mock_filters):
        """Test enforce with fail_open enabled."""
        mock_match = MagicMock()
        mock_match.rule_id = "RULE-001"
        mock_match.description = "Blocked"
        mock_match.severity = "MEDIUM"

        mock_filter_instance = MagicMock()
        mock_filter_instance.evaluate.return_value = MagicMock(
            allowed=False,
            blocking_matches=[mock_match],
            bypassed=False,
            sanitized_text="text",
        )
        mock_filter_instance.policy_path = None
        mock_filters.from_policy_file.return_value = mock_filter_instance

        settings = ModerationSettings(enabled=True, fail_open=True)
        adapter = ModerationAdapter(settings)

        # Should not raise even though rejected
        decision = adapter.enforce("content", stage="preflight")
        assert decision.approved is False, "approved is not valid"
        # But no exception raised


# =============================================================================
# Offline Filter Integration Tests
# =============================================================================


class TestOfflineFilterIntegration:
    """Tests for offline filter integration."""

    def test_offline_review_with_disabled_moderation(self):
        """Test offline review when moderation is disabled."""
        settings = ModerationSettings(enabled=False)
        adapter = ModerationAdapter(settings)

        decision = adapter.review("any content", stage="preflight")

        assert decision.approved is True, "approved is not valid"
        assert decision.provider == "disabled", "provider is not valid"

    def test_offline_review_enabled_returns_decision(self):
        """Test that offline review returns a decision."""
        settings = ModerationSettings(enabled=True, provider="offline")
        adapter = ModerationAdapter(settings)

        decision = adapter.review("test content", stage="preflight")

        # Should return a decision object
        assert isinstance(decision, ModerationDecision)
        assert decision.stage == "preflight", "stage is not valid"
        assert decision.provider == "offline", "provider is not valid"


# =============================================================================
# Provider Integration Tests
# =============================================================================


class TestProviderIntegration:
    """Tests for external provider integration."""

    def test_normalize_payload_decision_object(self):
        """Test normalizing ModerationDecision object."""
        original_decision = ModerationDecision(
            approved=True,
            stage="preflight",
            provider="custom",
        )

        settings = ModerationSettings(enabled=True)
        adapter = ModerationAdapter(settings)

        normalized = adapter._normalize_payload(original_decision, "preflight")

        assert normalized == original_decision, "normalized is not valid"

    def test_normalize_payload_dict(self):
        """Test normalizing dict payload."""
        payload = {
            "approved": True,
            "matches": ["pattern1", "pattern2"],
            "reasons": ["safe", "clean"],
            "provider": "external",
            "sanitized_text": "clean text",
            "extra_field": "extra_value",
        }

        settings = ModerationSettings(enabled=True)
        adapter = ModerationAdapter(settings)

        decision = adapter._normalize_payload(payload, "preflight")

        assert decision.approved is True, "approved is not valid"
        assert len(decision.matches) == 2, "Collection must not be empty"
        assert len(decision.reasons) == 2, "Collection must not be empty"
        assert decision.provider == "external", "provider is not valid"
        assert decision.sanitized_text == "clean text", "sanitized_text is not valid"
        assert decision.details["extra_field"] == "extra_value", "Value must be initialized"

    def test_normalize_payload_minimal_dict(self):
        """Test normalizing minimal dict payload."""
        payload = {"approved": False}

        settings = ModerationSettings(enabled=True)
        adapter = ModerationAdapter(settings)

        decision = adapter._normalize_payload(payload, "preflight")

        assert decision.approved is False, "approved is not valid"
        assert decision.matches == (), "matches is not valid"
        assert decision.reasons == (), "reasons is not valid"

    def test_normalize_payload_invalid_type(self):
        """Test normalizing invalid payload type."""
        settings = ModerationSettings(enabled=True)
        adapter = ModerationAdapter(settings)

        result = adapter._normalize_payload("invalid", "preflight")

        assert result is None, "Result must not be empty"


# =============================================================================
# Audit Logging Tests
# =============================================================================


class TestAuditLogging:
    """Tests for audit logging functionality."""

    def test_audit_log_setting(self):
        """Test audit log setting configuration."""
        audit_path = os.path.join(tempfile.gettempdir(), "test_audit.jsonl")
        settings = ModerationSettings(
            enabled=True,
            audit_log=audit_path,
        )
        adapter = ModerationAdapter(settings)

        assert adapter.settings.audit_log == audit_path, "audit_log is not valid"

    def test_audit_log_disabled_moderation(self):
        """Test that audit logging doesn't interfere when moderation disabled."""
        settings = ModerationSettings(
            enabled=False,
            audit_log=os.path.join(tempfile.gettempdir(), "audit.jsonl"),
        )
        adapter = ModerationAdapter(settings)

        decision = adapter.review("test", stage="preflight")
        assert decision.approved is True, "approved is not valid"


# =============================================================================
# Integration and Edge Case Tests
# =============================================================================


class TestIntegrationAndEdgeCases:
    """Integration tests and edge cases."""

    def test_end_to_end_approval_flow(self):
        """Test complete approval flow."""
        settings = ModerationSettings(enabled=False)
        adapter = ModerationAdapter(settings)

        # Review
        decision = adapter.review("safe content", stage="preflight")
        assert decision.approved is True, "approved is not valid"

        # Enforce
        result = adapter.enforce("safe content", stage="preflight")
        assert result.approved is True, "Result must not be empty"

    def test_end_to_end_rejection_flow(self):
        """Test complete rejection flow configuration."""
        # Test that settings can configure rejection behavior
        settings = ModerationSettings(enabled=True, fail_open=False)
        adapter = ModerationAdapter(settings)

        # Verify settings
        assert adapter.settings.fail_open is False, "fail_open is not valid"

    def test_different_stages(self):
        """Test moderation at different stages."""
        settings = ModerationSettings(enabled=False)
        adapter = ModerationAdapter(settings)

        stages = ["preflight", "postflight", "inline"]

        for stage in stages:
            decision = adapter.review("test", stage=stage)
            assert decision.stage == stage, "stage is not valid"

    def test_hash_text_utility(self):
        """Test text hashing utility."""
        settings = ModerationSettings()
        adapter = ModerationAdapter(settings)

        text1 = "Hello, world!"
        text2 = "Hello, world!"
        text3 = "Different text"

        hash1 = adapter._hash_text(text1)
        hash2 = adapter._hash_text(text2)
        hash3 = adapter._hash_text(text3)

        assert hash1 == hash2, "hash1 is not valid"
        assert hash1 != hash3, "hash1 is not valid"
        assert len(hash1) == 64, "Hash1 must not be empty"

    def test_very_long_text(self):
        """Test moderation with very long text."""
        settings = ModerationSettings(enabled=False)
        adapter = ModerationAdapter(settings)

        long_text = "test " * 100000
        decision = adapter.review(long_text, stage="preflight")

        assert decision.approved is True, "approved is not valid"

    def test_unicode_text(self):
        """Test moderation with unicode text."""
        settings = ModerationSettings(enabled=False)
        adapter = ModerationAdapter(settings)

        unicode_text = "Hello 世界 🌍 Привет"
        decision = adapter.review(unicode_text, stage="preflight")

        assert decision.approved is True, "approved is not valid"

    def test_empty_text(self):
        """Test moderation with empty text."""
        settings = ModerationSettings(enabled=False)
        adapter = ModerationAdapter(settings)

        decision = adapter.review("", stage="preflight")

        assert decision.approved is True, "approved is not valid"
