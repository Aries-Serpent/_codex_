"""Tests for the secret redaction utility."""

from __future__ import annotations

from codex_ml.safety.redaction import SecretRedactor


def test_redact_replaces_common_tokens():
    redactor = SecretRedactor()
    text = redactor.redact(
        "api_key=sk-123 password=supersecret user@example.com"
    )  # pragma: allowlist secret
    assert "[REDACTED_API_KEY]" in text, "Condition must be true"
    assert "[REDACTED_PASSWORD]" in text, "Condition must be true"
    assert "[REDACTED_EMAIL]" in text, "Condition must be true"


def test_redact_dict_handles_nested_mappings():
    redactor = SecretRedactor()
    payload = {
        "api_key": "sk-123",  # pragma: allowlist secret
        "nested": {"password": "letmein"},  # pragma: allowlist secret
        "public": "ok",
    }
    result = redactor.redact_dict(payload)
    assert result["api_key"].startswith("[REDACTED_API_KEY]"), "Result must not be empty"
    assert result["nested"]["password"].startswith("[REDACTED_PASSWORD]"), "Result must not be empty"
    assert result["public"] == "ok", "Result must not be empty"
