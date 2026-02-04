"""Regression tests for safety filters."""

from codex_ml.safety.filters import REDACT_TOKEN, SafetyFilters, SafetyPolicy


def _build_policy() -> SafetyPolicy:
    return SafetyPolicy.from_dict(
        {
            "enabled": True,
            "redaction_token": REDACT_TOKEN,
            "rules": [
                {
                    "id": "deny.sql.drop_database",
                    "action": "block",
                    "match": {"literal": "drop database"},
                },
                {
                    "id": "allow.sql.drop_schema_example",
                    "action": "allow",
                    "match": {"literal": "drop database schema_example"},
                },
            ],
        }
    )


def test_allow_rule_preserves_original_text_when_overriding_block():
    filters = SafetyFilters(_build_policy())
    text = "drop database schema_example"

    result = filters.evaluate(text)

    assert result.allowed is True
    assert result.sanitized_text == text


def test_block_rule_redacts_text_when_not_overridden():
    filters = SafetyFilters(_build_policy())
    text = "drop database production"

    result = filters.evaluate(text)

    assert result.allowed is False
    assert result.sanitized_text == "{REDACTED} production"


def test_allow_rule_retains_redactions_for_secret_matches():
    policy = SafetyPolicy.from_dict(
        {
            "enabled": True,
            "redaction_token": REDACT_TOKEN,
            "rules": [
                {
                    "id": "deny.sql.drop_database",
                    "action": "block",
                    "match": {"literal": "drop database"},
                },
                {
                    "id": "allow.sql.drop_schema_example",
                    "action": "allow",
                    "match": {"literal": "drop database schema_example"},
                },
                {
                    "id": "deny.secret.password_key",
                    "action": "redact",
                    "match": {"regex": "(?i)password\\s*[:=]\\s*[^\\s]+"},
                },
            ],
        }
    )
    filters = SafetyFilters(policy)
    text = "drop database schema_example password: hunter2"

    result = filters.evaluate(text)

    assert result.allowed is True
    assert result.sanitized_text == "drop database schema_example {REDACTED}"
