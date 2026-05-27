"""Phase E unit tests for services/msp_gateway/security.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest

# Ensure repo root is on sys.path so 'services.*' is importable
_REPO_ROOT = Path(__file__).resolve().parents[3]
_ROOT_SERVICES = str(_REPO_ROOT / "services")
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
try:
    import services as _svc_pkg
    if hasattr(_svc_pkg, "__path__") and _ROOT_SERVICES not in _svc_pkg.__path__:
        _svc_pkg.__path__.append(_ROOT_SERVICES)
except ImportError:
    pass

# ---------------------------------------------------------------------------
# PolicyEnforcer
# ---------------------------------------------------------------------------

class TestPolicyEnforcer:
    """Tests for PolicyEnforcer with mocked filesystem."""

    def _make_enforcer(self, safelist: dict | None = None, denylist: dict | None = None):
        """Return a PolicyEnforcer with policies injected directly."""
        from services.msp_gateway.security import PolicyEnforcer
        enforcer = PolicyEnforcer.__new__(PolicyEnforcer)
        enforcer.safelist = safelist or {}
        enforcer.denylist = denylist or {}
        return enforcer

    def test_check_blocked_patterns_no_denylist(self):
        enforcer = self._make_enforcer()
        result = enforcer.check_blocked_patterns("some safe text")
        assert result is None

    def test_check_blocked_patterns_match(self):
        enforcer = self._make_enforcer(
            denylist={"blocked_prompt_patterns": ["ignore previous instructions"]}
        )
        result = enforcer.check_blocked_patterns("Please ignore previous instructions now")
        assert result is not None
        assert "Blocked" in result

    def test_check_blocked_patterns_case_insensitive(self):
        enforcer = self._make_enforcer(
            denylist={"blocked_prompt_patterns": ["DROP TABLE"]}
        )
        result = enforcer.check_blocked_patterns("drop table users")
        assert result is not None

    def test_check_blocked_patterns_no_match(self):
        enforcer = self._make_enforcer(
            denylist={"blocked_prompt_patterns": ["evil pattern"]}
        )
        result = enforcer.check_blocked_patterns("totally benign text")
        assert result is None

    def test_check_blocked_actions_blocked(self):
        enforcer = self._make_enforcer(
            denylist={"blocked_actions": ["delete_all", "shutdown"]}
        )
        assert enforcer.check_blocked_actions("delete_all") is True
        assert enforcer.check_blocked_actions("shutdown") is True

    def test_check_blocked_actions_allowed(self):
        enforcer = self._make_enforcer(
            denylist={"blocked_actions": ["delete_all"]}
        )
        assert enforcer.check_blocked_actions("read_data") is False

    def test_check_blocked_actions_empty_denylist(self):
        enforcer = self._make_enforcer()
        assert enforcer.check_blocked_actions("anything") is False

    def test_redact_sensitive_content_disabled(self, monkeypatch):
        from services.msp_gateway.security import settings as sec_settings
        monkeypatch.setattr(sec_settings, "redaction_enabled", False)
        enforcer = self._make_enforcer()
        text = "my ssn is 123-45-6789"
        redacted, types_applied = enforcer.redact_sensitive_content(text)
        assert redacted == text
        assert types_applied == []

    def test_redact_sensitive_content_regex_pattern(self, monkeypatch):
        from services.msp_gateway.security import settings as sec_settings
        monkeypatch.setattr(sec_settings, "redaction_enabled", True)
        enforcer = self._make_enforcer(
            denylist={
                "redaction_patterns": [
                    {"pattern": r"\d{3}-\d{2}-\d{4}", "replacement": "[SSN]"}
                ],
                "sensitive_terms": [],
            }
        )
        text = "SSN is 123-45-6789 in file"
        redacted, applied = enforcer.redact_sensitive_content(text)
        assert "[SSN]" in redacted
        assert "[SSN]" in applied

    def test_redact_sensitive_terms(self, monkeypatch):
        from services.msp_gateway.security import settings as sec_settings
        monkeypatch.setattr(sec_settings, "redaction_enabled", True)
        enforcer = self._make_enforcer(
            denylist={
                "redaction_patterns": [],
                "sensitive_terms": ["password"],
            }
        )
        text = "My password is secret"
        redacted, applied = enforcer.redact_sensitive_content(text)
        assert "password" not in redacted.lower() or "[REDACTED]" in redacted
        assert any("term:password" in a for a in applied)

    def test_redact_no_match_no_change(self, monkeypatch):
        from services.msp_gateway.security import settings as sec_settings
        monkeypatch.setattr(sec_settings, "redaction_enabled", True)
        enforcer = self._make_enforcer(
            denylist={
                "redaction_patterns": [{"pattern": r"\b\d{16}\b", "replacement": "[CC]"}],
                "sensitive_terms": ["credit_card"],
            }
        )
        text = "Nothing sensitive here"
        redacted, applied = enforcer.redact_sensitive_content(text)
        assert redacted == text
        assert applied == []

    def test_load_policies_with_missing_files(self, tmp_path):
        """Loading with missing policy files logs warning but sets empty dicts."""
        from services.msp_gateway.security import PolicyEnforcer
        enforcer = PolicyEnforcer(policy_dir=str(tmp_path))
        assert enforcer.safelist == {}
        assert enforcer.denylist == {}

    def test_load_policies_with_valid_yaml(self, tmp_path):
        """Load policies from actual YAML files."""
        import yaml
        safelist_path = tmp_path / "safelist.yaml"
        denylist_path = tmp_path / "denylist.yaml"

        safelist_path.write_text(
            yaml.dump({"allowed_topics": ["coding", "science"]}),
            encoding="utf-8",
        )
        denylist_path.write_text(
            yaml.dump({"blocked_prompt_patterns": ["hack the"], "blocked_actions": []}),
            encoding="utf-8",
        )

        from services.msp_gateway.security import PolicyEnforcer
        enforcer = PolicyEnforcer(policy_dir=str(tmp_path))
        assert "allowed_topics" in enforcer.safelist
        assert "blocked_prompt_patterns" in enforcer.denylist


# ---------------------------------------------------------------------------
# AuthManager
# ---------------------------------------------------------------------------

class TestAuthManager:
    def _make_auth(self):
        from services.msp_gateway.security import AuthManager
        return AuthManager()

    def test_register_and_verify(self):
        auth = self._make_auth()
        auth.register_api_key("key123", "tenant_a")
        assert auth.verify_api_key("key123") == "tenant_a"

    def test_verify_unknown_key_returns_none(self):
        auth = self._make_auth()
        assert auth.verify_api_key("does-not-exist") is None

    def test_revoke_api_key(self):
        auth = self._make_auth()
        auth.register_api_key("key_to_revoke", "tenant_b")
        auth.revoke_api_key("key_to_revoke")
        assert auth.verify_api_key("key_to_revoke") is None

    def test_revoke_non_existent_key_no_error(self):
        auth = self._make_auth()
        auth.revoke_api_key("ghost_key")  # Should not raise

    def test_multiple_tenants(self):
        auth = self._make_auth()
        auth.register_api_key("k1", "t1")
        auth.register_api_key("k2", "t2")
        assert auth.verify_api_key("k1") == "t1"
        assert auth.verify_api_key("k2") == "t2"

    def test_overwrite_key(self):
        auth = self._make_auth()
        auth.register_api_key("key_shared", "tenant_old")
        auth.register_api_key("key_shared", "tenant_new")
        assert auth.verify_api_key("key_shared") == "tenant_new"


# ---------------------------------------------------------------------------
# OfflineGuard
# ---------------------------------------------------------------------------

class TestOfflineGuard:
    def _make_guard(self):
        from services.msp_gateway.security import OfflineGuard
        return OfflineGuard()

    def test_check_network_access_offline_true(self, monkeypatch):
        from services.msp_gateway.security import settings as sec_settings
        monkeypatch.setattr(sec_settings, "offline", True)
        guard = self._make_guard()
        assert guard.check_network_access() is True

    def test_check_network_access_offline_false(self, monkeypatch):
        from services.msp_gateway.security import settings as sec_settings
        monkeypatch.setattr(sec_settings, "offline", False)
        guard = self._make_guard()
        assert guard.check_network_access() is False

    def test_block_external_call_raises_when_offline(self, monkeypatch):
        from services.msp_gateway.security import settings as sec_settings
        monkeypatch.setattr(sec_settings, "offline", True)
        guard = self._make_guard()
        with pytest.raises(RuntimeError, match="offline mode"):
            guard.block_external_call("http_request")

    def test_block_external_call_passes_when_online(self, monkeypatch):
        from services.msp_gateway.security import settings as sec_settings
        monkeypatch.setattr(sec_settings, "offline", False)
        guard = self._make_guard()
        guard.block_external_call("http_request")  # Should not raise


# ---------------------------------------------------------------------------
# Module-level validate_prompt and redact_content
# ---------------------------------------------------------------------------

class TestModuleLevelFunctions:
    def test_validate_prompt_valid(self, monkeypatch):
        from services.msp_gateway import security
        # Inject a clean enforcer
        monkeypatch.setattr(
            security.policy_enforcer, "check_blocked_patterns", lambda _: None
        )
        valid, error = security.validate_prompt("Hello, world!", "tenant_x")
        assert valid is True
        assert error is None

    def test_validate_prompt_blocked(self, monkeypatch):
        from services.msp_gateway import security
        monkeypatch.setattr(
            security.policy_enforcer,
            "check_blocked_patterns",
            lambda _: "Blocked pattern detected: evil",
        )
        valid, error = security.validate_prompt("evil text", "tenant_x")
        assert valid is False
        assert error is not None

    def test_validate_prompt_too_long(self, monkeypatch):
        from services.msp_gateway import security
        monkeypatch.setattr(
            security.policy_enforcer, "check_blocked_patterns", lambda _: None
        )
        long_prompt = "a" * 10001
        valid, error = security.validate_prompt(long_prompt, "tenant_x")
        assert valid is False
        assert "maximum length" in (error or "")

    def test_redact_content_returns_tuple(self, monkeypatch):
        from services.msp_gateway import security
        monkeypatch.setattr(
            security.policy_enforcer,
            "redact_sensitive_content",
            lambda text: ("clean text", ["term:password"]),
        )
        text, redactions = security.redact_content("raw password text", "tenant_y")
        assert text == "clean text"
        assert "term:password" in redactions

    def test_redact_content_no_redactions(self, monkeypatch):
        from services.msp_gateway import security
        monkeypatch.setattr(
            security.policy_enforcer,
            "redact_sensitive_content",
            lambda text: (text, []),
        )
        text, redactions = security.redact_content("nothing sensitive", "tenant_z")
        assert text == "nothing sensitive"
        assert redactions == []
