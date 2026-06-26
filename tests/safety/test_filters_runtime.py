"""Runtime safety filter behavior tests."""

from codex_ml.safety.filters import SafetyFilters


def test_allow_does_not_override_unrelated_block():
    filters = SafetyFilters.from_defaults()
    text = "rm -rf / && rm -rf build"
    result = filters.evaluate(text)

    assert result.allowed is False, "Result must not be empty"
    assert "deny.shell.rm_root" in result.blocked_rules, "Result must not be empty"


def test_allow_overrides_specific_block_fragment():
    filters = SafetyFilters.from_defaults()
    text = "drop database schema_example"
    result = filters.evaluate(text)

    assert result.allowed is True, "Result must not be empty"
    assert "deny.sql.drop_database" not in result.blocked_rules, "Result must not be empty"
