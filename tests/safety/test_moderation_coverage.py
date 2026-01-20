"""
Tests for src/codex_ml/safety/moderation.py

This module contains comprehensive tests for the moderation system.
Covers ModerationSettings, ModerationDecision, ModerationAdapter, and rejection handling.

Test Coverage Target: 20+ tests for ~80% coverage of moderation module.

Created: 2026-01-18 (Phase 14.2)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Import module under test
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


# Skip all tests if module not available
pytestmark = pytest.mark.skipif(
    not MODERATION_AVAILABLE,
    reason="codex_ml.safety.moderation not available"
)


# =============================================================================
# ModerationSettings Tests
# =============================================================================


class TestModerationSettings:
    """Tests for ModerationSettings dataclass."""

    def test_default_values(self):
        """Test ModerationSettings default initialization."""
        settings = ModerationSettings()
        
        assert settings.enabled is False
        assert settings.provider == "offline"
        assert settings.rules_path is None
        assert settings.fail_open is False
        assert settings.audit_log is None
        assert settings.label == "default"

    def test_enabled_settings(self):
        """Test ModerationSettings with enabled=True."""
        settings = ModerationSettings(
            enabled=True,
            provider="openai",
            rules_path="/path/to/rules.yaml",
        )
        
        assert settings.enabled is True
        assert settings.provider == "openai"
        assert settings.rules_path == "/path/to/rules.yaml"

    def test_fail_open_setting(self):
        """Test fail_open configuration."""
        settings = ModerationSettings(
            enabled=True,
            fail_open=True,
        )
        
        assert settings.fail_open is True

    def test_audit_log_setting(self):
        """Test audit_log configuration."""
        settings = ModerationSettings(
            enabled=True,
            audit_log="/var/log/moderation.log",
        )
        
        assert settings.audit_log == "/var/log/moderation.log"

    def test_custom_label(self):
        """Test custom label configuration."""
        settings = ModerationSettings(
            label="production-filter",
        )
        
        assert settings.label == "production-filter"


# =============================================================================
# ModerationDecision Tests
# =============================================================================


class TestModerationDecision:
    """Tests for ModerationDecision dataclass."""

    def test_approved_decision(self):
        """Test creating an approved decision."""
        decision = ModerationDecision(
            approved=True,
            stage="preflight",
            provider="offline",
        )
        
        assert decision.approved is True
        assert decision.stage == "preflight"
        assert decision.provider == "offline"

    def test_rejected_decision(self):
        """Test creating a rejected decision."""
        decision = ModerationDecision(
            approved=False,
            stage="preflight",
            provider="openai",
            reasons=("harmful_content", "violence"),
            matches=("matched pattern 1",),
        )
        
        assert decision.approved is False
        assert decision.reasons == ("harmful_content", "violence")
        assert decision.matches == ("matched pattern 1",)

    def test_decision_with_sanitized_text(self):
        """Test decision with sanitized text."""
        decision = ModerationDecision(
            approved=True,
            stage="postflight",
            provider="offline",
            sanitized_text="[REDACTED] safe content",
        )
        
        assert decision.sanitized_text == "[REDACTED] safe content"

    def test_decision_with_details(self):
        """Test decision with additional details."""
        decision = ModerationDecision(
            approved=True,
            stage="preflight",
            provider="custom",
            details={"score": 0.95, "categories": ["safe"]},
        )
        
        assert decision.details["score"] == 0.95
        assert decision.details["categories"] == ["safe"]

    def test_to_dict(self):
        """Test converting decision to dictionary."""
        decision = ModerationDecision(
            approved=True,
            stage="preflight",
            provider="offline",
            reasons=("clean",),
            matches=(),
            sanitized_text="text",
            details={"key": "value"},
        )
        
        result = decision.to_dict()
        
        assert isinstance(result, dict)
        assert result["approved"] is True
        assert result["stage"] == "preflight"
        assert result["provider"] == "offline"
        assert result["reasons"] == ["clean"]
        assert result["matches"] == []
        assert result["sanitized_text"] == "text"
        assert result["details"] == {"key": "value"}

    def test_default_empty_tuples(self):
        """Test default empty tuples for reasons and matches."""
        decision = ModerationDecision(
            approved=True,
            stage="preflight",
            provider="offline",
        )
        
        assert decision.reasons == ()
        assert decision.matches == ()

    def test_default_empty_details(self):
        """Test default empty dict for details."""
        decision = ModerationDecision(
            approved=True,
            stage="preflight",
            provider="offline",
        )
        
        assert decision.details == {}


# =============================================================================
# ModerationRejection Tests
# =============================================================================


class TestModerationRejection:
    """Tests for ModerationRejection exception."""

    def test_exception_inheritance(self):
        """Test ModerationRejection inherits from RuntimeError."""
        assert issubclass(ModerationRejection, RuntimeError)

    def test_basic_rejection(self):
        """Test basic rejection exception."""
        decision = ModerationDecision(
            approved=False,
            stage="preflight",
            provider="offline",
            matches=("harmful_content",),
        )
        
        rejection = ModerationRejection("preflight", decision)
        
        assert rejection.stage == "preflight"
        assert rejection.decision == decision
        assert "harmful_content" in str(rejection)

    def test_rejection_with_reasons(self):
        """Test rejection with reasons instead of matches."""
        decision = ModerationDecision(
            approved=False,
            stage="postflight",
            provider="openai",
            reasons=("violence", "hate_speech"),
        )
        
        rejection = ModerationRejection("postflight", decision)
        
        assert "violence" in str(rejection) or "hate_speech" in str(rejection)

    def test_rejection_with_provider_error(self):
        """Test rejection with provider error."""
        decision = ModerationDecision(
            approved=False,
            stage="preflight",
            provider="external",
        )
        error = Exception("API timeout")
        
        rejection = ModerationRejection(
            "preflight",
            decision,
            provider_error=error,
        )
        
        assert rejection.provider_error == error

    def test_rejection_empty_matches_and_reasons(self):
        """Test rejection message with empty matches and reasons."""
        decision = ModerationDecision(
            approved=False,
            stage="preflight",
            provider="offline",
        )
        
        rejection = ModerationRejection("preflight", decision)
        
        assert "moderation policy" in str(rejection)


# =============================================================================
# ModerationAdapter Tests
# =============================================================================


class TestModerationAdapter:
    """Tests for ModerationAdapter class."""

    def test_create_with_default_settings(self):
        """Test creating adapter with default settings."""
        settings = ModerationSettings()
        adapter = ModerationAdapter(settings)
        
        assert adapter.settings == settings

    def test_create_with_enabled_settings(self):
        """Test creating adapter with enabled moderation."""
        settings = ModerationSettings(
            enabled=True,
            provider="offline",
        )
        adapter = ModerationAdapter(settings)
        
        assert adapter.settings.enabled is True

    def test_create_with_default_policy(self):
        """Test creating adapter with default policy."""
        settings = ModerationSettings()
        adapter = ModerationAdapter(settings, default_policy="strict")
        
        assert adapter._default_policy == "strict"

    @patch.object(ModerationAdapter, '_resolve_provider')
    def test_provider_resolution(self, mock_resolve):
        """Test provider resolution during initialization."""
        mock_resolve.return_value = None
        settings = ModerationSettings(provider="custom")
        
        adapter = ModerationAdapter(settings)
        
        mock_resolve.assert_called_once_with("custom")


# =============================================================================
# Integration Tests
# =============================================================================


class TestModerationIntegration:
    """Integration tests for moderation components."""

    def test_decision_in_rejection(self):
        """Test that decision object is properly included in rejection."""
        decision = ModerationDecision(
            approved=False,
            stage="preflight",
            provider="offline",
            reasons=("dangerous_content",),
            details={"score": 0.1},
        )
        
        rejection = ModerationRejection("preflight", decision)
        
        # Verify we can access decision details from rejection
        assert rejection.decision.details["score"] == 0.1
        assert rejection.decision.reasons == ("dangerous_content",)

    def test_settings_to_adapter_flow(self):
        """Test settings being used by adapter."""
        settings = ModerationSettings(
            enabled=True,
            provider="offline",
            fail_open=True,
            label="test-adapter",
        )
        adapter = ModerationAdapter(settings)
        
        assert adapter.settings.fail_open is True
        assert adapter.settings.label == "test-adapter"

    def test_decision_dict_roundtrip(self):
        """Test decision to_dict produces consistent output."""
        decision1 = ModerationDecision(
            approved=True,
            stage="preflight",
            provider="offline",
            reasons=("clean",),
            matches=("safe_pattern",),
            sanitized_text="clean text",
            details={"confidence": 0.99},
        )
        
        dict1 = decision1.to_dict()
        
        # Create another decision from same parameters
        decision2 = ModerationDecision(
            approved=dict1["approved"],
            stage=dict1["stage"],
            provider=dict1["provider"],
            reasons=tuple(dict1["reasons"]),
            matches=tuple(dict1["matches"]),
            sanitized_text=dict1["sanitized_text"],
            details=dict1["details"],
        )
        
        dict2 = decision2.to_dict()
        
        assert dict1 == dict2


# =============================================================================
# Edge Cases
# =============================================================================


class TestModerationEdgeCases:
    """Edge case tests for moderation components."""

    def test_empty_provider_string(self):
        """Test settings with empty provider string."""
        settings = ModerationSettings(provider="")
        # Should not crash
        assert settings.provider == ""

    def test_very_long_reasons(self):
        """Test decision with very long reason strings."""
        long_reason = "a" * 10000
        decision = ModerationDecision(
            approved=False,
            stage="preflight",
            provider="offline",
            reasons=(long_reason,),
        )
        
        assert len(decision.reasons[0]) == 10000

    def test_unicode_in_matches(self):
        """Test decision with unicode in matches."""
        decision = ModerationDecision(
            approved=False,
            stage="preflight",
            provider="offline",
            matches=("危険なコンテンツ", "опасный контент"),
        )
        
        assert "危険なコンテンツ" in decision.matches
        assert "опасный контент" in decision.matches

    def test_decision_with_none_sanitized_text(self):
        """Test decision with None sanitized_text (default)."""
        decision = ModerationDecision(
            approved=True,
            stage="postflight",
            provider="offline",
        )
        
        assert decision.sanitized_text is None
        
        dict_form = decision.to_dict()
        assert dict_form["sanitized_text"] is None

    def test_multiple_stages(self):
        """Test decisions for different stages."""
        stages = ["preflight", "postflight", "inline", "custom"]
        
        for stage in stages:
            decision = ModerationDecision(
                approved=True,
                stage=stage,
                provider="offline",
            )
            assert decision.stage == stage

    def test_rejection_preserves_stage(self):
        """Test that rejection preserves the stage information."""
        for stage in ["preflight", "postflight"]:
            decision = ModerationDecision(
                approved=False,
                stage=stage,
                provider="offline",
            )
            rejection = ModerationRejection(stage, decision)
            assert rejection.stage == stage
            assert f"{stage}" in str(rejection)

    def test_settings_all_fields_set(self):
        """Test settings with all fields explicitly set."""
        settings = ModerationSettings(
            enabled=True,
            provider="custom-provider",
            rules_path="/custom/rules.yaml",
            fail_open=True,
            audit_log="/custom/audit.log",
            label="custom-label",
        )
        
        assert settings.enabled is True
        assert settings.provider == "custom-provider"
        assert settings.rules_path == "/custom/rules.yaml"
        assert settings.fail_open is True
        assert settings.audit_log == "/custom/audit.log"
        assert settings.label == "custom-label"
