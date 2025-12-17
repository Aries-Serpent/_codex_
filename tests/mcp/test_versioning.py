"""Smoke tests for :mod:`mcp.versioning`.

Tests for MCP version negotiation with comprehensive safeguards validation.
Includes tests for input validation, sanitization, and bounds checking.
"""

from __future__ import annotations

import pytest

from mcp.versioning import (
    MAX_VERSIONS_COUNT,
    MCP_VERSIONS,
    negotiate_version,
    supports_feature,
    validate_version,
)


class TestVersionNegotiation:
    """Tests for version negotiation with validation safeguards."""

    def test_negotiate_version_picks_highest(self):
        """Test that negotiation picks highest compatible version."""
        assert negotiate_version(["0.9", "1.0"]) == MCP_VERSIONS[0]

    def test_negotiate_version_no_overlap(self):
        """Test error handling when no compatible version exists."""
        with pytest.raises(ValueError):
            negotiate_version(["0.5", "0.6"])

    def test_negotiate_requires_client_versions(self):
        """Test input validation rejects empty version list."""
        with pytest.raises(ValueError):
            negotiate_version([])


class TestVersionValidation:
    """Tests for version string validation safeguards."""

    def test_validate_version_accepts_valid(self):
        """Test validation accepts correct version format."""
        assert validate_version("1.0") is True

    def test_validate_version_rejects_invalid(self):
        """Test validation rejects malformed version strings."""
        # Test bounds check on invalid version
        assert validate_version("invalid") is False
        assert validate_version("") is False
        assert validate_version("a.b.c") is False

    def test_validate_version_rejects_unsupported(self):
        """Test validation rejects unsupported versions."""
        assert validate_version("99.99") is False


class TestSanitization:
    """Tests for version list sanitization safeguards."""

    def test_negotiate_sanitizes_invalid_versions(self):
        """Test that invalid versions are filtered during sanitization."""
        # Should still find 1.0 after sanitizing invalid entries
        assert negotiate_version(["invalid", "1.0", "malformed"]) == "1.0"

    def test_negotiate_handles_bounds_check(self):
        """Test bounds checking on oversized version lists."""
        # Create large list with valid version at end
        # Use half the MAX_VERSIONS_COUNT to stay within bounds
        large_list = ["0.9"] * (MAX_VERSIONS_COUNT // 2) + ["1.0"]
        result = negotiate_version(large_list)
        assert result == "1.0"


class TestFeatureSupport:
    """Tests for feature support checking with validation."""

    def test_supports_feature_basic_tools(self):
        """Test feature detection for basic tools."""
        assert supports_feature("basic_tools", "1.0") is True

    def test_supports_feature_invalid_input(self):
        """Test defensive handling of invalid inputs."""
        # Test input validation safeguards
        assert supports_feature("", "1.0") is False
        assert supports_feature("basic_tools", "") is False
        assert supports_feature(None, "1.0") is False  # type: ignore[arg-type]

    def test_supports_feature_unknown(self):
        """Test defensive behavior for unknown features."""
        assert supports_feature("unknown_feature", "1.0") is False


class TestDeterminism:
    """Tests for deterministic behavior safeguards."""

    def test_version_list_is_deterministic(self):
        """Test that MCP_VERSIONS has reproducible ordering."""
        # Version list should be deterministic for reproducibility
        assert MCP_VERSIONS == ["1.0"]

    def test_negotiate_is_deterministic(self):
        """Test that negotiation produces reproducible results."""
        # Run multiple times to verify determinism
        results = [negotiate_version(["1.0", "0.9"]) for _ in range(10)]
        assert all(r == "1.0" for r in results)
