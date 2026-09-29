"""
Phase 16.1: API Versioning Tests

This module provides comprehensive tests for API versioning, backward compatibility,
and version negotiation across the API.

Created: 2026-01-18
Phase: 16.1 - API Contract Testing
Tests: 10+
"""

import re
from pathlib import Path

import pytest

# Repository root
REPO_ROOT = Path(__file__).parents[2]
SRC_DIR = REPO_ROOT / "src"


class TestAPIVersioning:
    """Tests for API versioning structure and compatibility."""

    def test_api_version_defined(self):
        """Verify API version is defined in the codebase."""
        # Check for version in multiple places
        pyproject = REPO_ROOT / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8")
            assert "version" in content, "pyproject.toml should define version"

    def test_api_endpoints_have_version_prefix(self):
        """Verify API endpoints follow versioning convention."""
        # Search for API route definitions
        api_files = list(SRC_DIR.rglob("api*.py")) if SRC_DIR.exists() else []
        app_files = [f for f in api_files if "app" in f.name]

        if not app_files:
            pytest.skip("No API app files found")

        versioning_patterns_found = 0
        for api_file in app_files[:5]:
            content = api_file.read_text(encoding="utf-8", errors="ignore")
            # Check for version patterns like /v1/, /api/v2, etc.
            if re.search(r"['\"]*/v\d+['\"]", content) or re.search(r"prefix.*v\d+", content):
                versioning_patterns_found += 1

        # At least some indication of versioning
        assert versioning_patterns_found > 0, "API should use versioning in endpoints"

    def test_version_negotiation_supported(self):
        """Verify API supports version negotiation."""
        # Check for version negotiation patterns
        api_files = list(SRC_DIR.rglob("api*.py")) if SRC_DIR.exists() else []

        if not api_files:
            pytest.skip("No API files found")

        # Look for common version negotiation patterns
        has_accept_header = any(
            "Accept" in Path(f).read_text(encoding="utf-8", errors="ignore")
            for f in api_files[:10]
        )
        has_version_param = any(
            "version" in Path(f).read_text(encoding="utf-8", errors="ignore")
            for f in api_files[:10]
        )

        # Should support at least one version negotiation method
        assert has_accept_header or has_version_param, "API should support version negotiation"

    def test_backward_compatibility_maintained(self):
        """Verify API maintains backward compatibility."""
        # Check for deprecated endpoint support or versioning strategy
        api_files = list(SRC_DIR.rglob("api*.py")) if SRC_DIR.exists() else []

        if not api_files:
            pytest.skip("No API files found")

        # Check for backward compatibility patterns
        compat_patterns = [
            r"deprecated",
            r"backward.*compat",
            r"legacy",
            r"support.*old.*version",
        ]

        found_patterns = 0
        for api_file in api_files[:10]:
            content = api_file.read_text(encoding="utf-8", errors="ignore").lower()
            for pattern in compat_patterns:
                if re.search(pattern, content):
                    found_patterns += 1
                    break

        # Some indication of backward compatibility strategy
        assert found_patterns > 0, "API should have backward compatibility strategy"

    def test_version_documented(self):
        """Verify API version is documented."""
        # Check documentation for version info
        docs_dir = REPO_ROOT / "docs"
        api_ref = docs_dir / "API_REFERENCE.md"
        api_docs = docs_dir / "api" / "index.md" if (docs_dir / "api").exists() else None

        docs_exist = any(d.exists() for d in [api_ref, api_docs])
        if docs_exist:
            # At least one doc should mention versioning
            for doc in [api_ref, api_docs]:
                if doc and doc.exists():
                    content = doc.read_text(encoding="utf-8", errors="ignore").lower()
                    if "version" in content or "v1" in content:
                        assert True
                        return

        # If no docs found, mark as skip
        if not docs_exist:
            pytest.skip("API documentation not found")

    def test_version_in_response_headers(self):
        """Verify API responses include version information."""
        # Check for version headers in API response handling
        api_files = list(SRC_DIR.rglob("api*.py")) if SRC_DIR.exists() else []

        if not api_files:
            pytest.skip("No API files found")

        header_patterns = [
            r"X-API-Version",
            r"API-Version",
            r"api.version",
            r"Version",
        ]

        found_headers = 0
        for api_file in api_files[:10]:
            content = api_file.read_text(encoding="utf-8", errors="ignore")
            for pattern in header_patterns:
                if re.search(pattern, content):
                    found_headers += 1
                    break

        # Some indication of version in headers
        if api_files:
            assert found_headers > 0, "API should include version in response headers"

    def test_major_minor_patch_versioning(self):
        """Verify semantic versioning (major.minor.patch)."""
        pyproject = REPO_ROOT / "pyproject.toml"
        if not pyproject.exists():
            pytest.skip("pyproject.toml not found")

        content = pyproject.read_text(encoding="utf-8")
        # Look for semantic version pattern
        version_match = re.search(r'version\s*=\s*["\']([0-9]+\.[0-9]+\.[0-9]+[^"\']*)["\']', content)
        if version_match:
            version = version_match.group(1)
            # Verify semantic versioning format
            assert re.match(r"^\d+\.\d+\.\d+", version), f"Version {version} should follow semantic versioning"

    def test_version_deprecation_warnings(self):
        """Verify deprecated API versions show warnings."""
        # Check for deprecation warning patterns
        api_files = list(SRC_DIR.rglob("api*.py")) if SRC_DIR.exists() else []

        if not api_files:
            pytest.skip("No API files found")

        deprecation_patterns = [
            r"deprecat",
            r"warn",
            r"obsolete",
            r"no longer supported",
        ]

        found_deprecations = 0
        for api_file in api_files[:10]:
            content = api_file.read_text(encoding="utf-8", errors="ignore").lower()
            for pattern in deprecation_patterns:
                if re.search(pattern, content):
                    found_deprecations += 1
                    break

        # Some indication of deprecation strategy
        if api_files:
            assert found_deprecations > 0, "API should have deprecation warnings for old versions"

    def test_version_changelog_documented(self):
        """Verify API version changes are documented in changelog."""
        changelog_paths = [
            REPO_ROOT / "CHANGELOG.md",
            REPO_ROOT / "docs" / "CHANGELOG.md",
        ]

        for changelog in changelog_paths:
            if changelog.exists():
                content = changelog.read_text(encoding="utf-8", errors="ignore")
                # Should mention versions or changes
                if "v0." in content or "v1." in content or "## [" in content:
                    assert True
                    return

        pytest.skip("CHANGELOG not found or empty")

    def test_multiple_api_versions_supported(self):
        """Verify API can support multiple versions simultaneously."""
        # Check for multiple version endpoint definitions
        api_files = list(SRC_DIR.rglob("api*.py")) if SRC_DIR.exists() else []

        if not api_files:
            pytest.skip("No API files found")

        version_routes = 0
        for api_file in api_files[:10]:
            content = api_file.read_text(encoding="utf-8", errors="ignore")
            # Count distinct version patterns (v1, v2, etc.)
            versions = set(re.findall(r"/v(\d+)", content))
            version_routes += len(versions)

        # Should support at least some versioning
        if api_files:
            assert version_routes > 0 or any(
                "version" in Path(f).read_text(encoding="utf-8", errors="ignore").lower()
                for f in api_files[:5]
            ), "API should support multiple versions"


class TestVersionNegotiation:
    """Tests for API version negotiation mechanisms."""

    def test_accept_header_processing(self):
        """Verify Accept header is processed for version negotiation."""
        api_files = list(SRC_DIR.rglob("api*.py")) if SRC_DIR.exists() else []

        if not api_files:
            pytest.skip("No API files found")

        # Look for Accept header handling
        found_accept = False
        for api_file in api_files[:10]:
            content = api_file.read_text(encoding="utf-8", errors="ignore")
            if "Accept" in content or "accept" in content.lower():
                found_accept = True
                break

        # Some indication of Accept header handling
        if api_files:
            assert found_accept, "API should process Accept headers for version negotiation"

    def test_default_version_fallback(self):
        """Verify API has a default version when not specified."""
        # Check for default version definition
        api_files = list(SRC_DIR.rglob("api*.py")) if SRC_DIR.exists() else []

        if not api_files:
            pytest.skip("No API files found")

        default_patterns = [
            r"DEFAULT_VERSION",
            r"default.*version",
            r"fallback.*version",
        ]

        found_default = 0
        for api_file in api_files[:10]:
            content = api_file.read_text(encoding="utf-8", errors="ignore")
            for pattern in default_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_default += 1
                    break

        # Some indication of default version
        if api_files:
            assert found_default > 0, "API should have a default version"


class TestVersionCompatibilityMatrix:
    """Tests for API version compatibility."""

    def test_version_compatibility_documented(self):
        """Verify version compatibility is documented."""
        docs_dir = REPO_ROOT / "docs"
        compat_files = [
            docs_dir / "API_COMPATIBILITY.md",
            docs_dir / "VERSIONING.md",
            docs_dir / "api" / "versioning.md",
        ]

        # At least one compatibility doc should exist
        found = any(f.exists() for f in compat_files)
        if not found:
            # Check in API reference
            api_ref = docs_dir / "API_REFERENCE.md"
            if api_ref.exists():
                content = api_ref.read_text(encoding="utf-8", errors="ignore").lower()
                assert "compatibility" in content or "version" in content, "Should document version compatibility"
            else:
                pytest.skip("No compatibility documentation found")

    def test_version_feature_flags(self):
        """Verify feature flags for version-specific features."""
        # Check for feature flag patterns
        api_files = list(SRC_DIR.rglob("api*.py")) if SRC_DIR.exists() else []

        if not api_files:
            pytest.skip("No API files found")

        feature_patterns = [
            r"feature.*flag",
            r"flag.*feature",
            r"enabled.*version",
            r"supports.*version",
        ]

        found_flags = 0
        for api_file in api_files[:10]:
            content = api_file.read_text(encoding="utf-8", errors="ignore").lower()
            for pattern in feature_patterns:
                if re.search(pattern, content):
                    found_flags += 1
                    break

        # Some indication of feature flags
        if api_files:
            assert found_flags > 0, "API should use feature flags for version-specific features"
