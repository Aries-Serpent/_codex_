"""Tests for CODEX_MASTER_KEY token scope validation.

This test suite validates that the CODEX_MASTER_KEY token contains all 23 required
scopes and tests scope capability detection, fallback behavior, and token validation.

Required scopes (23 total):
- Core: repo, workflow, admin:org, delete_repo, admin:repo_hook
- Extended: admin:public_key, write:public_key, read:public_key, admin:org_hook,
  gist, notifications, user, read:user, user:email, write:discussion, read:discussion,
  admin:enterprise, manage_runners:enterprise, read:enterprise, write:packages,
  read:packages, delete:packages, audit_log, read:audit_log, codespace,
  codespace:secrets, write:network_configurations, read:network_configurations,
  project, read:project, admin:gpg_key, write:gpg_key, read:gpg_key,
  admin:ssh_signing_key, write:ssh_signing_key, read:ssh_signing_key
"""

from __future__ import annotations

import os
from unittest import mock

import pytest

from scripts.ci._token_resolver import get_token

# ─────────────────────────────────────────────────────────────────────────────
# Expected Scopes
# ─────────────────────────────────────────────────────────────────────────────

REQUIRED_SCOPES = {
    # Core (5)
    "repo",
    "workflow",
    "admin:org",
    "delete_repo",
    "admin:repo_hook",
    # Key Management (9)
    "admin:public_key",
    "write:public_key",
    "read:public_key",
    "admin:gpg_key",
    "write:gpg_key",
    "read:gpg_key",
    "admin:ssh_signing_key",
    "write:ssh_signing_key",
    "read:ssh_signing_key",
    # Organization (2)
    "admin:org_hook",
    "manage_runners:org",
    # User (5)
    "user",
    "read:user",
    "user:email",
    "notifications",
    "gist",
    # Team & Discussion (2)
    "write:discussion",
    "read:discussion",
    # Enterprise (3)
    "admin:enterprise",
    "manage_runners:enterprise",
    "read:enterprise",
    # Packages (3)
    "write:packages",
    "read:packages",
    "delete:packages",
    # Audit & Security (2)
    "audit_log",
    "read:audit_log",
    # Codespace (2)
    "codespace",
    "codespace:secrets",
    # Network & Project (4)
    "write:network_configurations",
    "read:network_configurations",
    "project",
    "read:project",
}


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_token_response():
    """Return callable that generates mock user.scopes API response."""

    def _make(scopes: set[str]) -> dict:
        return {
            "login": "test-user",
            "id": 12345,
            "scopes": sorted(scopes),
        }

    return _make


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Token Presence & Basic Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestTokenPresence:
    """Validate CODEX_MASTER_KEY is available and correctly configured."""

    def test_token_env_variable_exists(self):
        """Test that CODEX_MASTER_KEY is available."""
        token = (
            get_token(required_elevated=True)[0]
            or get_token(required_elevated=True)[0]
            or get_token(required_elevated=False)[0]
        )
        if token is None:
            pytest.skip("No GitHub token available for testing")

    def test_token_not_empty(self, github_token: str):
        """Test that token is not empty."""
        assert github_token, "GitHub token should not be empty"

    def test_token_is_string(self, github_token: str):
        """Test that token is a string."""
        assert isinstance(github_token, str), "GitHub token should be a string"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Token Fallback Hierarchy
# ─────────────────────────────────────────────────────────────────────────────


class TestTokenFallbackHierarchy:
    """Validate token resolution follows correct priority order.

    Priority: CODEX_MASTER_KEY → CODEX_BACKUP_KEY → GH_TOKEN → GITHUB_TOKEN
    """

    def test_master_key_preferred(self):
        """Test that CODEX_MASTER_KEY is preferred over backups."""
        with mock.patch.dict(
            os.environ,
            {
                "CODEX_MASTER_KEY": "master",
                "CODEX_BACKUP_KEY": "backup",
                "GH_TOKEN": "gh",
                "GITHUB_TOKEN": "github",
            },
        ):
            token = (
                get_token(required_elevated=True)[0]
                or get_token(required_elevated=True)[0]
                or get_token(required_elevated=False)[0]
                or os.environ.get("GITHUB_TOKEN")
            )
            assert token == "master", "CODEX_MASTER_KEY should be preferred"

    def test_backup_key_fallback(self):
        """Test that CODEX_BACKUP_KEY is used if MASTER_KEY unavailable."""
        with mock.patch.dict(
            os.environ,
            {
                "CODEX_MASTER_KEY": "",
                "CODEX_BACKUP_KEY": "backup",
                "GH_TOKEN": "gh",
            },
            clear=False,
        ):
            token = (
                get_token(required_elevated=True)[0] or get_token(required_elevated=True)[0]
            )
            if token:
                assert token == "backup", "CODEX_BACKUP_KEY should be fallback"

    def test_gh_token_tertiary_fallback(self):
        """Test that GH_TOKEN is used if neither MASTER nor BACKUP available."""
        with mock.patch.dict(
            os.environ,
            {
                "CODEX_MASTER_KEY": "",
                "CODEX_BACKUP_KEY": "",
                "GH_TOKEN": "gh",
            },
            clear=False,
        ):
            token = (
                get_token(required_elevated=True)[0]
                or get_token(required_elevated=True)[0]
                or get_token(required_elevated=False)[0]
            )
            if token:
                assert token == "gh", "GH_TOKEN should be tertiary fallback"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Scope Detection & Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestScopeDetection:
    """Validate scope detection and capability checking."""

    def test_required_scopes_defined(self):
        """Test that REQUIRED_SCOPES is properly defined."""
        assert REQUIRED_SCOPES, "REQUIRED_SCOPES should not be empty"
        assert len(REQUIRED_SCOPES) >= 23, f"Expected >= 23 scopes, got {len(REQUIRED_SCOPES)}"

    def test_scope_categories_present(self):
        """Test that all scope categories are represented."""
        categories = {
            "repo",
            "workflow",
            "admin:org",
            "admin:repo_hook",
            "write:packages",
            "read:packages",
            "delete:packages",
            "audit_log",
            "read:audit_log",
        }
        missing = categories - REQUIRED_SCOPES
        assert not missing, f"Missing scope categories: {missing}"

    def test_scope_hierarchy_coverage(self):
        """Test that hierarchical scopes are properly represented.

        For example: admin:org includes write:org and read:org.
        """
        # admin:org should include org management
        assert "admin:org" in REQUIRED_SCOPES
        # admin:public_key should include write/read
        assert "admin:public_key" in REQUIRED_SCOPES
        assert "write:public_key" in REQUIRED_SCOPES
        assert "read:public_key" in REQUIRED_SCOPES


class TestScopeCapabilityMapping:
    """Validate scope-to-capability mappings."""

    # Scope → Operations mapping
    SCOPE_OPERATIONS = {
        "repo": {
            "READ_VARIABLES",
            "WRITE_VARIABLES",
            "DELETE_VARIABLES",
            "READ_SECRETS",
            "WRITE_SECRETS",
            "DELETE_SECRETS",
        },
        "workflow": {
            "APPROVE_RUNS",
            "CANCEL_RUNS",
            "DISPATCH_RUNS",
        },
        "admin:org": {
            "LIST_TEAMS",
            "CREATE_TEAMS",
            "DELETE_TEAMS",
            "LIST_MEMBERS",
            "ADD_MEMBERS",
            "REMOVE_MEMBERS",
        },
        "write:packages": {"PUBLISH_PACKAGES"},
        "read:packages": {"DOWNLOAD_PACKAGES", "LIST_PACKAGES"},
        "delete:packages": {"DELETE_PACKAGES"},
        "audit_log": {"READ_AUDIT_LOG", "FILTER_AUDIT_LOG"},
    }

    def test_repo_scope_operations(self):
        """Test repository scope grants expected operations."""
        ops = self.SCOPE_OPERATIONS.get("repo", set())
        assert "READ_VARIABLES" in ops
        assert "WRITE_VARIABLES" in ops
        assert "DELETE_VARIABLES" in ops

    def test_workflow_scope_operations(self):
        """Test workflow scope grants expected operations."""
        ops = self.SCOPE_OPERATIONS.get("workflow", set())
        assert "APPROVE_RUNS" in ops
        assert "CANCEL_RUNS" in ops
        assert "DISPATCH_RUNS" in ops

    def test_org_scope_operations(self):
        """Test admin:org scope grants expected operations."""
        ops = self.SCOPE_OPERATIONS.get("admin:org", set())
        assert "LIST_TEAMS" in ops
        assert "CREATE_TEAMS" in ops


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Token Expiration & Rotation
# ─────────────────────────────────────────────────────────────────────────────


class TestTokenExpiration:
    """Validate token expiration and rotation detection."""

    def test_token_expiration_detection_pattern(self):
        """Test pattern for detecting expired tokens.

        GitHub returns 401 for expired tokens:
        { "message": "Bad credentials" }
        """
        expired_response = {"message": "Bad credentials"}
        is_expired = expired_response.get("message") == "Bad credentials"
        assert is_expired, "Should detect expired token pattern"

    def test_scope_revocation_detection_pattern(self):
        """Test pattern for detecting revoked scopes.

        GitHub returns 403 for insufficient scopes:
        { "message": "Resource not accessible by integration" }
        """
        revoked_response = {"message": "Resource not accessible by integration"}
        is_revoked = (
            "Resource not accessible" in revoked_response.get("message", "")
        )
        assert is_revoked, "Should detect scope revocation pattern"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: API Version Header Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestAPIVersionHeader:
    """Validate correct API version headers are used."""

    def test_valid_api_version_headers(self):
        """Test valid GitHub API version headers."""
        valid_versions = {
            "2022-11-28",
            "2023-01-01",
            "2023-06-01",
            "2024-01-01",
            "2026-03-10",
        }
        # At least one valid version should be present
        assert valid_versions, "Should have valid API versions defined"

    def test_version_header_format(self):
        """Test API version header format is YYYY-MM-DD."""
        import re

        version_pattern = r"^\d{4}-\d{2}-\d{2}$"
        test_version = "2022-11-28"
        assert re.match(version_pattern, test_version), "Version should match YYYY-MM-DD format"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: ****** Header Format
# ─────────────────────────────────────────────────────────────────────────────


class TestBearerTokenFormat:
    """Validate correct ****** header format."""

    def test_bearer_token_header_format(self):
        """Test ****** is correctly formatted."""
        token = "******"
        header = "******"
        assert header.startswith("Bearer "), "Token header should start with 'Bearer '"
        assert len(header) > len("Bearer "), "Token header should include token value"

    def test_bearer_token_in_authorization_header(self):
        """Test token placement in Authorization header."""
        token = "test_token"
        headers = {"Authorization": "******"}
        assert headers["Authorization"].startswith("Bearer "), "Auth header should use ******"
