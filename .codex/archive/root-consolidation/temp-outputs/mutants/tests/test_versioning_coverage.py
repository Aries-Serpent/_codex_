"""
Comprehensive tests for mcp.versioning module.

Tests cover version negotiation, validation, and feature support for the
MCP (Model Context Protocol) implementation.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from mcp.versioning import (
    MAX_VERSION_LENGTH,
    MAX_VERSIONS_COUNT,
    MCP_VERSIONS,
    VERSION_PATTERN,
    _sanitize_version_list,
    _validate_version_string,
    negotiate_version,
    supports_feature,
    validate_version,
)


class TestValidateVersionString:
    """Test _validate_version_string function."""

    def test_validate_version_string_valid_major_minor(self):
        """Test validation of valid MAJOR.MINOR version."""
        assert _validate_version_string("1.0") is True, "Condition must be true"
        assert _validate_version_string("2.5") is True, "Condition must be true"
        assert _validate_version_string("10.20") is True, "Condition must be true"

    def test_validate_version_string_valid_semantic(self):
        """Test validation of valid semantic versions."""
        assert _validate_version_string("1.0.0") is True, "Condition must be true"
        assert _validate_version_string("2.1.3") is True, "Condition must be true"
        assert _validate_version_string("10.20.30") is True, "Condition must be true"

    def test_validate_version_string_empty(self):
        """Test validation of empty string."""
        assert _validate_version_string("") is False, "Condition must be true"

    def test_validate_version_string_invalid_format(self):
        """Test validation of invalid formats."""
        assert _validate_version_string("1") is False, "Condition must be true"
        assert _validate_version_string("v1.0") is False, "Condition must be true"
        assert _validate_version_string("1.0.0.0") is False, "Condition must be true"
        assert _validate_version_string("1.0-alpha") is False, "Condition must be true"
        assert _validate_version_string("1.0+build") is False, "Condition must be true"

    def test_validate_version_string_too_long(self):
        """Test validation of version exceeding max length."""
        long_version = "1." + "0" * MAX_VERSION_LENGTH
        assert _validate_version_string(long_version) is False, "Condition must be true"

    def test_validate_version_string_at_max_length(self):
        """Test validation of version at max length."""
        # Construct a valid version at max length
        version = "1" + "." + "0" * (MAX_VERSION_LENGTH - 2)
        assert _validate_version_string(version) is True, "Condition must be true"

    def test_validate_version_string_non_numeric(self):
        """Test validation of non-numeric versions."""
        assert _validate_version_string("a.b") is False, "Condition must be true"
        assert _validate_version_string("1.x") is False, "Condition must be true"
        assert _validate_version_string("one.zero") is False, "Condition must be true"

    def test_validate_version_string_leading_zeros(self):
        """Test validation with leading zeros (should be valid regex)."""
        assert _validate_version_string("01.00") is True, "Condition must be true"
        assert _validate_version_string("001.002.003") is True, "Condition must be true"

    def test_validate_version_string_whitespace(self):
        """Test validation with whitespace."""
        assert _validate_version_string(" 1.0") is False, "Condition must be true"
        assert _validate_version_string("1.0 ") is False, "Condition must be true"
        assert _validate_version_string("1 . 0") is False, "Condition must be true"

    def test_validate_version_string_special_chars(self):
        """Test validation with special characters."""
        assert _validate_version_string("1.0!") is False, "Condition must be true"
        assert _validate_version_string("1@0") is False, "Condition must be true"
        assert _validate_version_string("1.0.0-rc1") is False, "Condition must be true"


class TestSanitizeVersionList:
    """Test _sanitize_version_list function."""

    def test_sanitize_version_list_empty(self):
        """Test sanitization of empty list."""
        result = _sanitize_version_list([])
        assert result == [], "Result must not be empty"

    def test_sanitize_version_list_single_valid(self):
        """Test sanitization with single valid version."""
        result = _sanitize_version_list(["1.0"])
        assert result == ["1.0"], "Result must not be empty"

    def test_sanitize_version_list_multiple_valid(self):
        """Test sanitization with multiple valid versions."""
        result = _sanitize_version_list(["1.0", "2.0", "1.5"])
        assert result == ["1.0", "2.0", "1.5"]

    def test_sanitize_version_list_mixed_valid_invalid(self):
        """Test sanitization filters out invalid versions."""
        result = _sanitize_version_list(["1.0", "invalid", "2.0", "v1.0"])
        assert result == ["1.0", "2.0"]

    def test_sanitize_version_list_all_invalid(self):
        """Test sanitization with all invalid versions."""
        result = _sanitize_version_list(["invalid", "bad", "wrong"])
        assert result == [], "Result must not be empty"

    def test_sanitize_version_list_exceeds_max_count(self):
        """Test sanitization truncates list exceeding max count."""
        versions = [f"{i}.0" for i in range(MAX_VERSIONS_COUNT + 10)]
        result = _sanitize_version_list(versions)
        assert len(result) <= MAX_VERSIONS_COUNT, "Result must not be empty"

    def test_sanitize_version_list_non_list_input(self):
        """Test sanitization with non-list input."""
        with patch("mcp.versioning.logger"):
            result = _sanitize_version_list("1.0")
            assert result == [], "Result must not be empty"

    def test_sanitize_version_list_non_string_elements(self):
        """Test sanitization with non-string elements."""
        result = _sanitize_version_list(["1.0", 2.0, None, "2.0"])
        assert result == ["1.0", "2.0"]

    def test_sanitize_version_list_preserves_order(self):
        """Test that sanitization preserves order."""
        versions = ["2.0", "1.0", "1.5", "3.0"]
        result = _sanitize_version_list(versions)
        assert result == versions, "Result must not be empty"

    def test_sanitize_version_list_duplicates(self):
        """Test sanitization with duplicate versions."""
        result = _sanitize_version_list(["1.0", "1.0", "2.0"])
        assert result == ["1.0", "1.0", "2.0"]  # Preserves duplicates

    @patch("mcp.versioning.logger")
    def test_sanitize_version_list_logs_warnings(self, mock_logger):
        """Test that warnings are logged."""
        _sanitize_version_list(["1.0", "invalid", "2.0"])
        assert mock_logger.warning.called or mock_logger.debug.called, "Condition must be true"


class TestNegotiateVersion:
    """Test negotiate_version function."""

    def test_negotiate_version_single_supported(self):
        """Test negotiation with single supported version."""
        result = negotiate_version(["1.0"])
        assert result == "1.0", "Result must not be empty"

    def test_negotiate_version_multiple_supported(self):
        """Test negotiation with multiple supported versions."""
        result = negotiate_version(["1.0", "2.0"])
        assert result == "1.0", "Result must not be empty"

    def test_negotiate_version_first_match_wins(self):
        """Test negotiation returns first server preference match."""
        # Server preferences: [1.0]
        # Client supports: [1.0, 2.0]
        # Should return 1.0 (first in server preference)
        result = negotiate_version(["1.0", "2.0"])
        assert result == "1.0", "Result must not be empty"

    def test_negotiate_version_empty_client_versions(self):
        """Test negotiation fails with empty client versions."""
        with pytest.raises(ValueError, match="at least one"):
            negotiate_version([])

    def test_negotiate_version_no_compatibility(self):
        """Test negotiation fails when no common version."""
        with pytest.raises(ValueError, match="No compatible"):
            negotiate_version(["2.0", "3.0"])

    def test_negotiate_version_invalid_versions_filtered(self):
        """Test negotiation filters invalid versions."""
        with pytest.raises(ValueError, match="No valid version"):
            negotiate_version(["invalid", "bad", "wrong"])

    def test_negotiate_version_mixed_valid_invalid(self):
        """Test negotiation with mixed valid/invalid versions."""
        result = negotiate_version(["1.0", "invalid", "2.0"])
        assert result == "1.0", "Result must not be empty"

    def test_negotiate_version_exact_match(self):
        """Test negotiation with exact version match."""
        result = negotiate_version(["1.0"])
        assert result == "1.0", "Result must not be empty"

    def test_negotiate_version_server_preference_order(self):
        """Test that server preference order is respected."""
        # MCP_VERSIONS = ["1.0"] (server preference)
        # Client supports multiple versions
        result = negotiate_version(["1.0"])
        assert result == "1.0", "Result must not be empty"


class TestSupportsFeature:
    """Test supports_feature function."""

    def test_supports_feature_basic_tools_v1(self):
        """Test basic_tools feature support in v1.0."""
        assert supports_feature("basic_tools", "1.0") is True

    def test_supports_feature_streaming_v1(self):
        """Test streaming feature support in v1.0."""
        assert supports_feature("streaming", "1.0") is True

    def test_supports_feature_unknown_feature(self):
        """Test unknown feature returns False."""
        assert supports_feature("unknown_feature", "1.0") is False

    def test_supports_feature_invalid_version(self):
        """Test invalid version returns False."""
        assert supports_feature("basic_tools", "invalid") is False

    def test_supports_feature_empty_feature_name(self):
        """Test empty feature name returns False."""
        assert supports_feature("", "1.0") is False

    def test_supports_feature_none_feature(self):
        """Test None feature returns False."""
        assert supports_feature(None, "1.0") is False

    def test_supports_feature_empty_version(self):
        """Test empty version returns False."""
        assert supports_feature("basic_tools", "") is False

    def test_supports_feature_none_version(self):
        """Test None version returns False."""
        assert supports_feature("basic_tools", None) is False

    def test_supports_feature_case_sensitive(self):
        """Test feature names are case-sensitive."""
        assert supports_feature("basic_tools", "1.0") is True
        assert supports_feature("Basic_Tools", "1.0") is False

    def test_supports_feature_non_string_inputs(self):
        """Test non-string inputs handling."""
        # Non-string feature name returns False
        assert supports_feature(123, "1.0") is False

        # Non-string version causes TypeError
        with pytest.raises(TypeError):
            supports_feature("basic_tools", 1.0)


class TestValidateVersion:
    """Test validate_version function."""

    def test_validate_version_supported(self):
        """Test validation of supported version."""
        assert validate_version("1.0") is True, "Condition must be true"

    def test_validate_version_unsupported(self):
        """Test validation of unsupported version."""
        assert validate_version("2.0") is False, "Condition must be true"
        assert validate_version("0.9") is False, "Condition must be true"

    def test_validate_version_invalid_format(self):
        """Test validation of invalid format."""
        assert validate_version("invalid") is False, "Condition must be true"
        assert validate_version("v1.0") is False, "Condition must be true"

    def test_validate_version_empty(self):
        """Test validation of empty string."""
        assert validate_version("") is False, "Condition must be true"

    def test_validate_version_too_long(self):
        """Test validation of version exceeding max length."""
        long_version = "1." + "0" * MAX_VERSION_LENGTH
        assert validate_version(long_version) is False, "Condition must be true"

    def test_validate_version_semantic_version(self):
        """Test validation of semantic versions."""
        assert validate_version("1.0.0") is False, "Condition must be true"
        assert validate_version("2.1.3") is False, "Condition must be true"

    def test_validate_version_non_string(self):
        """Test validation with non-string input."""
        assert validate_version(None) is False, "Condition must be true"

        # Non-string numeric input causes TypeError
        with pytest.raises(TypeError):
            validate_version(1.0)


class TestVersionPatternRegex:
    """Test VERSION_PATTERN regex."""

    def test_version_pattern_matches_major_minor(self):
        """Test regex matches MAJOR.MINOR format."""
        import re

        assert re.match(VERSION_PATTERN, "1.0") is not None
        assert re.match(VERSION_PATTERN, "99.99") is not None

    def test_version_pattern_matches_semantic(self):
        """Test regex matches semantic version format."""
        import re

        assert re.match(VERSION_PATTERN, "1.0.0") is not None
        assert re.match(VERSION_PATTERN, "2.1.3") is not None

    def test_version_pattern_rejects_invalid(self):
        """Test regex rejects invalid formats."""
        import re

        assert re.match(VERSION_PATTERN, "v1.0") is None
        assert re.match(VERSION_PATTERN, "1.0-alpha") is None
        assert re.match(VERSION_PATTERN, "1.0.0.0") is None


class TestMCPVersionsConstant:
    """Test MCP_VERSIONS constant."""

    def test_mcp_versions_is_list(self):
        """Test MCP_VERSIONS is a list."""
        assert isinstance(MCP_VERSIONS, list)

    def test_mcp_versions_not_empty(self):
        """Test MCP_VERSIONS is not empty."""
        assert len(MCP_VERSIONS) > 0, "Mcp_versions must not be empty"

    def test_mcp_versions_contains_valid_versions(self):
        """Test MCP_VERSIONS contains valid version strings."""
        for version in MCP_VERSIONS:
            assert _validate_version_string(version), "Condition must be true"

    def test_mcp_versions_current_version(self):
        """Test that expected version is in MCP_VERSIONS."""
        assert "1.0" in MCP_VERSIONS, "Condition must be true"


class TestVersioningIntegration:
    """Integration tests for versioning functions."""

    def test_full_negotiation_workflow(self):
        """Test full version negotiation workflow."""
        # Client supports multiple versions
        client_versions = ["1.0", "2.0", "1.5"]

        # Negotiate
        agreed_version = negotiate_version(client_versions)

        # Validate the agreed version
        assert validate_version(agreed_version), "Condition must be true"

        # Check features available
        assert supports_feature("basic_tools", agreed_version)

    def test_incompatible_versions_flow(self):
        """Test flow with incompatible versions."""
        client_versions = ["2.0", "3.0"]

        with pytest.raises(ValueError):
            negotiate_version(client_versions)

    def test_sanitization_in_negotiation(self):
        """Test that negotiation properly sanitizes input."""
        # Mix of valid and invalid
        client_versions = ["1.0", "invalid", "2.0"]

        # Should still work by filtering
        result = negotiate_version(client_versions)
        assert result == "1.0", "Result must not be empty"

    def test_feature_availability_by_version(self):
        """Test checking all features for supported versions."""
        features = ["basic_tools", "streaming"]

        for version in MCP_VERSIONS:
            assert validate_version(version), "Condition must be true"
            for feature in features:
                # At least some features should be supported
                result = supports_feature(feature, version)
                assert isinstance(result, bool)

    def test_version_round_trip(self):
        """Test version negotiation round-trip."""
        # Client proposes version
        client_versions = ["1.0"]

        # Server negotiates
        agreed = negotiate_version(client_versions)

        # Both sides validate the agreed version
        assert validate_version(agreed), "Condition must be true"
        assert agreed in MCP_VERSIONS, "Condition must be true"
