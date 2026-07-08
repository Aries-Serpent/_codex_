"""
Tests for knob parsing utility (scripts/config/parse_knobs.py).
"""

import os

import pytest

from scripts.config.parse_knobs import (
    clear_warnings,
    get_allowlist_extensions,
    get_allowlist_profile,
    get_archive_format,
    get_archive_pointer_style,
    get_auto_archive_enabled,
    get_bundle_prefix_mode,
    get_content_filter_mode,
    get_depth,
    get_max_bundle_mb,
    get_pii_custom_list,
    get_pii_mode,
    get_pii_pattern_set,
    get_pii_regex_strategy,
    get_warnings,
    parse_csv_list,
    parse_enum,
    parse_int,
    parse_truthy,
)


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before each test."""
    env_vars = [
        "AUDIT_DEPTH",
        "AUDIT_DEPTH_DEFAULT",
        "PII_MODE",
        "PII_PATTERN_SET",
        "PII_CUSTOM_LIST",
        "PII_REGEX_STRATEGY",
        "CONTENT_FILTER_MODE",
        "ALLOWLIST_PROFILE",
        "ALLOWLIST_EXT",
        "MAX_BUNDLE_MB",
        "AUTO_ARCHIVE_DISABLE",
        "ARCHIVE_FORMAT",
        "ARCHIVE_POINTER_STYLE",
        "BUNDLE_PREFIX_MODE",
    ]
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]

    clear_warnings()
    yield

    # Cleanup after test
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
    clear_warnings()


class TestParseTruthy:
    """Tests for parse_truthy function."""

    def test_truthy_values(self):
        assert parse_truthy("1") is True, "Condition must be true"
        assert parse_truthy("true") is True, "Condition must be true"
        assert parse_truthy("TRUE") is True, "Condition must be true"
        assert parse_truthy("yes") is True, "Condition must be true"
        assert parse_truthy("Y") is True, "Condition must be true"
        assert parse_truthy("on") is True, "Condition must be true"

    def test_falsy_values(self):
        assert parse_truthy("0") is False, "Condition must be true"
        assert parse_truthy("false") is False, "Condition must be true"
        assert parse_truthy("FALSE") is False, "Condition must be true"
        assert parse_truthy("no") is False, "Condition must be true"
        assert parse_truthy("n") is False, "Condition must be true"
        assert parse_truthy("off") is False, "Condition must be true"
        assert parse_truthy("") is False, "Condition must be true"

    def test_none_uses_default(self):
        assert parse_truthy(None, default=True) is True
        assert parse_truthy(None, default=False) is False

    def test_invalid_uses_default(self):
        assert parse_truthy("invalid", default=True) is True
        assert parse_truthy("invalid", default=False) is False


class TestParseEnum:
    """Tests for parse_enum function."""

    def test_valid_value(self):
        result = parse_enum("A", ["A", "B", "C"], "B", "TEST_VAR")
        assert result == "A", "Result must not be empty"
        assert len(get_warnings()) == 0, "Collection must not be empty"

    def test_invalid_value_uses_default(self):
        clear_warnings()
        result = parse_enum("X", ["A", "B", "C"], "B", "TEST_VAR")
        assert result == "B", "Result must not be empty"
        warnings = get_warnings()
        assert len(warnings) == 1, "Warnings must not be empty"
        assert "invalid_value:TEST_VAR" in warnings[0], "Value must be initialized"

    def test_none_uses_default(self):
        clear_warnings()
        result = parse_enum(None, ["A", "B", "C"], "B", "TEST_VAR")
        assert result == "B", "Result must not be empty"
        warnings = get_warnings()
        assert len(warnings) == 1, "Warnings must not be empty"
        assert "required_selection_missing:TEST_VAR" in warnings[0], "Condition must be true"


class TestParseCSVList:
    """Tests for parse_csv_list function."""

    def test_valid_csv(self):
        result = parse_csv_list("a,b,c")
        assert result == ["a", "b", "c"]

    def test_csv_with_spaces(self):
        result = parse_csv_list("a , b , c")
        assert result == ["a", "b", "c"]

    def test_empty_string(self):
        result = parse_csv_list("")
        assert result == [], "Result must not be empty"

    def test_none(self):
        result = parse_csv_list(None)
        assert result == [], "Result must not be empty"

    def test_single_value(self):
        result = parse_csv_list("single")
        assert result == ["single"], "Result must not be empty"


class TestParseInt:
    """Tests for parse_int function."""

    def test_valid_int(self):
        assert parse_int("42", 10) == 42

    def test_invalid_int_uses_default(self):
        assert parse_int("not_a_number", 10) == 10

    def test_none_uses_default(self):
        assert parse_int(None, 10) == 10

    def test_empty_string_uses_default(self):
        assert parse_int("", 10) == 10

    def test_with_min_bound(self):
        assert parse_int("5", 10, min_val=1) == 5
        assert parse_int("0", 10, min_val=1) == 10  # Below min

    def test_with_max_bound(self):
        assert parse_int("5", 10, max_val=10) == 5
        assert parse_int("15", 10, max_val=10) == 10  # Above max


class TestDepthKnobs:
    """Tests for depth-related knobs."""

    def test_explicit_depth_full(self):
        os.environ["AUDIT_DEPTH"] = "4"
        depth, warning_issued = get_depth()
        assert depth == 4, "depth is not valid"
        assert warning_issued is False, "warning_issued is not valid"

    def test_explicit_depth_restricted(self):
        os.environ["AUDIT_DEPTH"] = "3"
        clear_warnings()
        depth, warning_issued = get_depth()
        assert depth == 3, "depth is not valid"
        assert warning_issued is True, "warning_issued is not valid"
        warnings = get_warnings()
        assert any("depth_restriction_active" in w for w in warnings), "Condition must be true"

    def test_default_depth_used(self):
        os.environ["AUDIT_DEPTH_DEFAULT"] = "3"
        clear_warnings()
        depth, _warning_issued = get_depth()
        assert depth == 3, "depth is not valid"
        warnings = get_warnings()
        assert any("depth_default_used" in w for w in warnings), "Condition must be true"

    def test_no_depth_set_uses_hardcoded_default(self):
        clear_warnings()
        depth, _warning_issued = get_depth()
        assert depth == 3, "depth is not valid"
        warnings = get_warnings()
        assert any("depth_default_used" in w for w in warnings), "Condition must be true"


class TestPIIKnobs:
    """Tests for PII-related knobs."""

    def test_pii_mode_default(self):
        clear_warnings()
        mode = get_pii_mode()
        assert mode == "union-minimal", "mode is not valid"
        warnings = get_warnings()
        assert any("required_selection_missing:PII_MODE" in w for w in warnings), "Condition must be true"

    def test_pii_mode_explicit(self):
        os.environ["PII_MODE"] = "union-extended"
        clear_warnings()
        mode = get_pii_mode()
        assert mode == "union-extended", "mode is not valid"
        assert len(get_warnings()) == 0, "Collection must not be empty"

    def test_pii_pattern_set_default(self):
        clear_warnings()
        pattern_set = get_pii_pattern_set()
        assert pattern_set == "minimal", "pattern_set is not valid"

    def test_pii_custom_list_empty(self):
        custom = get_pii_custom_list()
        assert custom == [], "custom is not valid"

    def test_pii_custom_list_with_values(self):
        os.environ["PII_CUSTOM_LIST"] = "pattern1,pattern2,pattern3"
        custom = get_pii_custom_list()
        assert custom == ["pattern1", "pattern2", "pattern3"]

    def test_pii_regex_strategy_default(self):
        strategy = get_pii_regex_strategy()
        assert strategy == "skip-manifest", "strategy is not valid"


class TestContentFilterKnobs:
    """Tests for content filter knobs."""

    def test_content_filter_mode_default(self):
        mode = get_content_filter_mode()
        assert mode == "allowlist", "mode is not valid"

    def test_allowlist_profile_default(self):
        clear_warnings()
        profile = get_allowlist_profile()
        assert profile == "A", "profile is not valid"
        warnings = get_warnings()
        assert any("allowlist_default_used" in w for w in warnings), "Condition must be true"

    def test_allowlist_profile_explicit(self):
        os.environ["ALLOWLIST_PROFILE"] = "B"
        clear_warnings()
        profile = get_allowlist_profile()
        assert profile == "B", "profile is not valid"
        assert len(get_warnings()) == 0, "Collection must not be empty"

    def test_allowlist_extensions_empty(self):
        extensions = get_allowlist_extensions()
        assert extensions == [], "extensions is not valid"

    def test_allowlist_extensions_with_values(self):
        os.environ["ALLOWLIST_EXT"] = ".log,.conf,.ini"
        extensions = get_allowlist_extensions()
        assert extensions == [".log", ".conf", ".ini"]


class TestArchivalKnobs:
    """Tests for archival-related knobs."""

    def test_max_bundle_mb_default(self):
        max_mb = get_max_bundle_mb()
        assert max_mb == 25, "max_mb is not valid"

    def test_max_bundle_mb_custom(self):
        os.environ["MAX_BUNDLE_MB"] = "50"
        max_mb = get_max_bundle_mb()
        assert max_mb == 50, "max_mb is not valid"

    def test_auto_archive_enabled_default(self):
        enabled = get_auto_archive_enabled()
        assert enabled is True, "enabled is not valid"

    def test_auto_archive_disabled(self):
        os.environ["AUTO_ARCHIVE_DISABLE"] = "1"
        clear_warnings()
        enabled = get_auto_archive_enabled()
        assert enabled is False, "enabled is not valid"
        warnings = get_warnings()
        assert any("auto_archive_disabled" in w for w in warnings), "Condition must be true"

    def test_archive_format_default(self):
        fmt = get_archive_format()
        assert fmt == "tar.gz", "fmt is not valid"

    def test_archive_format_zip(self):
        os.environ["ARCHIVE_FORMAT"] = "zip"
        fmt = get_archive_format()
        assert fmt == "zip", "fmt is not valid"

    def test_archive_pointer_style_default(self):
        style = get_archive_pointer_style()
        assert style == "both", "style is not valid"

    def test_bundle_prefix_mode_default(self):
        mode = get_bundle_prefix_mode()
        assert mode is False, "mode is not valid"

    def test_bundle_prefix_mode_enabled(self):
        os.environ["BUNDLE_PREFIX_MODE"] = "1"
        mode = get_bundle_prefix_mode()
        assert mode is True, "mode is not valid"


class TestWarningAccumulation:
    """Tests for warning accumulation across multiple knob reads."""

    def test_multiple_warnings_accumulated(self):
        # Don't set any env vars - multiple defaults will trigger warnings
        clear_warnings()

        get_pii_mode()  # Call to trigger PII mode warning
        get_allowlist_profile()  # Call to trigger allowlist profile warning
        _depth, _ = get_depth()  # Triggers warnings

        warnings = get_warnings()
        assert len(warnings) >= 2, "Warnings must not be empty"

    def test_clear_warnings_works(self):
        clear_warnings()
        _ = get_pii_mode()  # Triggers warning
        assert len(get_warnings()) > 0, "Collection must not be empty"

        clear_warnings()
        assert len(get_warnings()) == 0, "Collection must not be empty"
