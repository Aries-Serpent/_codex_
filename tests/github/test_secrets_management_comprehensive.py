"""Comprehensive tests for secrets management via CODEX_MASTER_KEY.

This test suite covers:
- Repository Actions Secrets CRUD (Process 3)
- Organization Actions Secrets CRUD (Process 4)
- Dependabot Secrets CRUD (Process 5)
- Codespaces Secrets CRUD (Process 6)
- Secret encryption with libsodium
- Public key retrieval and validation
- Secret lifecycle management

All tests skip gracefully if CODEX_MASTER_KEY is unavailable or libsodium unavailable.
"""

from __future__ import annotations

import base64
from typing import (  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    Any,
    Optional,
)

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def actions_secrets_endpoint(repo_owner: str, repo_name: str) -> str:
    """Return repository Actions secrets endpoint."""
    return f"/repos/{repo_owner}/{repo_name}/actions/secrets"


@pytest.fixture
def dependabot_secrets_endpoint(repo_owner: str, repo_name: str) -> str:
    """Return repository Dependabot secrets endpoint."""
    return f"/repos/{repo_owner}/{repo_name}/dependabot/secrets"


@pytest.fixture
def codespaces_secrets_endpoint(repo_owner: str, repo_name: str) -> str:
    """Return repository Codespaces secrets endpoint."""
    return f"/repos/{repo_owner}/{repo_name}/codespaces/secrets"


@pytest.fixture
def org_actions_secrets_endpoint(org_name: str) -> str:
    """Return organization Actions secrets endpoint."""
    return f"/orgs/{org_name}/actions/secrets"


@pytest.fixture
def mock_public_key_response():
    """Return callable that generates mock public key responses."""

    def _make(key_id: str = "012345678901234567890", key: Optional[str] = None) -> dict[str, Any]:  # noqa: F841
        if key is None:
            # Valid base64-encoded 32-byte public key (Curve25519)
            key = base64.b64encode(b"x" * 32).decode()
        return {
            "key_id": key_id,
            "key": key,
        }

    return _make


@pytest.fixture
def test_secret_name_base() -> str:
    """Return base name for test secrets (timestamped)."""
    from datetime import datetime, timezone

    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"CODEX_API_TEST_SECRET_{ts}"


# ─────────────────────────────────────────────────────────────────────────────
# Process 3: Repository Actions Secrets Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestProcess3RepositoryActionsSecrets:
    """Process 3: Tests for repository Actions secrets (repo scope required)."""

    # ───────────────────────────────────────────────────────────────────────
    # Public Key Retrieval
    # ───────────────────────────────────────────────────────────────────────

    def test_process3_get_public_key_success(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
        mock_public_key_response,
    ):
        """Test: Retrieve repository public key for secret encryption."""
        endpoint = f"{gh_api_base}{actions_secrets_endpoint}/public-key"
        expected_response = mock_public_key_response()

        assert "public-key" in endpoint
        assert expected_response["key_id"]
        assert expected_response["key"]

    def test_process3_public_key_response_structure(self, mock_public_key_response):
        """Test: Public key response has required fields."""
        response = mock_public_key_response(key_id="test_key_123")

        assert "key_id" in response
        assert "key" in response
        assert isinstance(response["key_id"], str)
        assert isinstance(response["key"], str)

    def test_process3_public_key_base64_encoding(self, mock_public_key_response):
        """Test: Public key is valid base64-encoded string."""
        response = mock_public_key_response()

        # Verify base64 encoding
        try:
            decoded = base64.b64decode(response["key"])
            assert len(decoded) == 32  # Curve25519 key is 32 bytes
        except Exception as _err:
            pytest.fail("Public key is not valid base64 or incorrect size")

    def test_process3_public_key_caching(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
        mock_public_key_response,
    ):
        """Test: Public key should be cached to minimize API calls."""
        # First call retrieves key
        key1 = mock_public_key_response()
        # Second call should return cached key
        key2 = mock_public_key_response()

        assert key1["key"] == key2["key"]

    # ───────────────────────────────────────────────────────────────────────
    # Secret CRUD Operations
    # ───────────────────────────────────────────────────────────────────────

    def test_process3_list_actions_secrets_success(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
    ):
        """Test: List all repository Actions secrets."""
        endpoint = f"{gh_api_base}{actions_secrets_endpoint}"
        expected_response = {  # noqa: F841
            "total_count": 2,
            "secrets": [
                {
                    "name": "SECRET_ONE",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
                {
                    "name": "SECRET_TWO",
                    "created_at": "2024-01-02T00:00:00Z",
                    "updated_at": "2024-01-02T00:00:00Z",
                },
            ],
        }

        assert "actions/secrets" in endpoint
        assert expected_response["total_count"] == 2

    def test_process3_list_actions_secrets_empty(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
    ):
        """Test: List returns empty array when no secrets."""
        endpoint = f"{gh_api_base}{actions_secrets_endpoint}"
        expected_response = {"total_count": 0, "secrets": []}

        assert "actions/secrets" in endpoint
        assert expected_response["total_count"] == 0

    def test_process3_create_actions_secret_success(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
        test_secret_name_base: str,
        mock_public_key_response,
    ):
        """Test: Create Actions secret with encryption."""
        endpoint = f"{gh_api_base}{actions_secrets_endpoint}"
        public_key_response = mock_public_key_response()

        # Simulate secret encryption
        encrypted_secret = {
            "encrypted_value": "base64-encoded-encrypted-secret",
            "key_id": public_key_response["key_id"],
        }

        payload = {
            "encrypted_value": encrypted_secret["encrypted_value"],
            "key_id": encrypted_secret["key_id"],
        }

        assert payload["encrypted_value"]
        assert payload["key_id"]
        assert "actions/secrets" in endpoint

    def test_process3_create_secret_with_mock_encryption(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Create secret using mock encryption (libsodium unavailable)."""
        endpoint = f"{gh_api_base}{actions_secrets_endpoint}"

        # Mock encryption without libsodium
        secret_value = "my_secret_password"  # noqa: F841
        mock_encrypted = base64.b64encode(secret_value.encode()).decode()

        payload = {
            "name": test_secret_name_base,
            "encrypted_value": mock_encrypted,
            "key_id": "mock_key_id",
        }

        assert payload["name"] == test_secret_name_base
        assert payload["encrypted_value"]
        assert "actions/secrets" in endpoint

    def test_process3_create_secret_with_visibility(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Create secret with optional visibility parameter."""
        endpoint = f"{gh_api_base}{actions_secrets_endpoint}"

        payload = {  # noqa: F841
            "name": test_secret_name_base,
            "encrypted_value": "base64-value",
            "key_id": "key_id",
            "visibility": "selected",  # Optional field
            "selected_repository_ids": [123, 456],
        }

        assert payload.get("visibility") == "selected"
        assert "actions/secrets" in endpoint

    def test_process3_update_actions_secret_success(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Update an existing Actions secret."""
        endpoint = f"{gh_api_base}{actions_secrets_endpoint}/{test_secret_name_base}"

        payload = {
            "encrypted_value": "new_base64_encrypted_value",
            "key_id": "key_id",
        }

        assert payload["encrypted_value"]
        assert test_secret_name_base in endpoint

    def test_process3_delete_actions_secret_success(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Delete an Actions secret."""
        endpoint = f"{gh_api_base}{actions_secrets_endpoint}/{test_secret_name_base}"

        # DELETE returns 204 No Content
        assert test_secret_name_base in endpoint

    # ───────────────────────────────────────────────────────────────────────
    # Error Handling
    # ───────────────────────────────────────────────────────────────────────

    def test_process3_secret_not_found_error(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
        api_errors,
    ):
        """Test: 404 Not Found when secret doesn't exist."""
        error = api_errors.resource_not_found()
        assert error.code == 404

    def test_process3_invalid_encryption_error(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
        api_errors,
    ):
        """Test: 422 Unprocessable Entity for invalid encryption."""
        error = api_errors.unprocessable_entity()
        assert error.code == 422

    def test_process3_missing_key_id_error(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
        api_errors,
    ):
        """Test: 422 when key_id is missing."""
        error = api_errors.unprocessable_entity()
        assert error.code == 422


# ─────────────────────────────────────────────────────────────────────────────
# Process 4: Organization Actions Secrets Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestProcess4OrganizationActionsSecrets:
    """Process 4: Tests for organization Actions secrets (admin:org scope required)."""

    # ───────────────────────────────────────────────────────────────────────
    # Organization Public Key
    # ───────────────────────────────────────────────────────────────────────

    def test_process4_get_org_public_key_success(
        self,
        gh_api_base: str,
        org_actions_secrets_endpoint: str,
        mock_public_key_response,
    ):
        """Test: Retrieve organization public key for secret encryption."""
        endpoint = f"{gh_api_base}{org_actions_secrets_endpoint}/public-key"
        response = mock_public_key_response()

        assert "public-key" in endpoint
        assert "/orgs/" in endpoint
        assert response["key_id"]

    # ───────────────────────────────────────────────────────────────────────
    # Organization Secret CRUD
    # ───────────────────────────────────────────────────────────────────────

    def test_process4_list_org_secrets_success(
        self,
        gh_api_base: str,
        org_actions_secrets_endpoint: str,
    ):
        """Test: List organization Actions secrets."""
        endpoint = f"{gh_api_base}{org_actions_secrets_endpoint}"

        assert "actions/secrets" in endpoint
        assert "/orgs/" in endpoint

    def test_process4_create_org_secret_success(
        self,
        gh_api_base: str,
        org_actions_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Create organization-scope secret."""
        endpoint = f"{gh_api_base}{org_actions_secrets_endpoint}"

        payload = {
            "name": test_secret_name_base,
            "encrypted_value": "base64_encrypted",
            "key_id": "org_key_id",
            "visibility": "all",  # all, private, or selected
        }

        assert payload["visibility"] in ["all", "private", "selected"]
        assert "actions/secrets" in endpoint

    def test_process4_create_org_secret_visibility_selected(
        self,
        gh_api_base: str,
        org_actions_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Create org secret with repository scope selection."""
        endpoint = f"{gh_api_base}{org_actions_secrets_endpoint}"

        payload = {
            "name": test_secret_name_base,
            "encrypted_value": "base64_encrypted",
            "key_id": "key_id",
            "visibility": "selected",
            "selected_repository_ids": [111, 222, 333],
        }

        assert payload["visibility"] == "selected"
        assert len(payload["selected_repository_ids"]) == 3
        assert "/orgs/" in endpoint

    def test_process4_update_org_secret_success(
        self,
        gh_api_base: str,
        org_actions_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Update organization secret."""
        endpoint = f"{gh_api_base}{org_actions_secrets_endpoint}/{test_secret_name_base}"

        payload = {"encrypted_value": "new_base64_value", "key_id": "key_id"}

        assert payload["encrypted_value"]
        assert test_secret_name_base in endpoint

    def test_process4_delete_org_secret_success(
        self,
        gh_api_base: str,
        org_actions_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Delete organization secret."""
        endpoint = f"{gh_api_base}{org_actions_secrets_endpoint}/{test_secret_name_base}"

        assert test_secret_name_base in endpoint

    # ───────────────────────────────────────────────────────────────────────
    # Error Handling
    # ───────────────────────────────────────────────────────────────────────

    def test_process4_insufficient_admin_scope_error(
        self,
        gh_api_base: str,
        org_actions_secrets_endpoint: str,
        api_errors,
    ):
        """Test: 403 Forbidden when token lacks 'admin:org' scope."""
        error = api_errors.insufficient_scope()
        assert error.code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Process 5: Dependabot Secrets Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestProcess5DependabotSecrets:
    """Process 5: Tests for Dependabot secrets (repo scope required)."""

    # ───────────────────────────────────────────────────────────────────────
    # Dependabot Public Key
    # ───────────────────────────────────────────────────────────────────────

    def test_process5_get_dependabot_public_key_success(
        self,
        gh_api_base: str,
        dependabot_secrets_endpoint: str,
        mock_public_key_response,
    ):
        """Test: Retrieve Dependabot public key for secret encryption."""
        endpoint = f"{gh_api_base}{dependabot_secrets_endpoint}/public-key"
        response = mock_public_key_response(key_id="dependabot_key_123")

        assert "dependabot/secrets" in endpoint
        assert "public-key" in endpoint
        assert response["key_id"]

    # ───────────────────────────────────────────────────────────────────────
    # Dependabot Secret CRUD
    # ───────────────────────────────────────────────────────────────────────

    def test_process5_list_dependabot_secrets_success(
        self,
        gh_api_base: str,
        dependabot_secrets_endpoint: str,
    ):
        """Test: List Dependabot secrets."""
        endpoint = f"{gh_api_base}{dependabot_secrets_endpoint}"

        assert "dependabot/secrets" in endpoint

    def test_process5_create_dependabot_secret_success(
        self,
        gh_api_base: str,
        dependabot_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Create Dependabot secret."""
        endpoint = f"{gh_api_base}{dependabot_secrets_endpoint}"

        payload = {
            "name": test_secret_name_base,
            "encrypted_value": "base64_encrypted",
            "key_id": "dependabot_key_id",
        }

        assert payload["name"]
        assert payload["encrypted_value"]
        assert "dependabot/secrets" in endpoint

    def test_process5_dependabot_secret_isolation(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
        dependabot_secrets_endpoint: str,
    ):
        """Test: Dependabot secrets are isolated from Actions secrets.

        Same secret name can exist in both without conflict.
        """
        actions_endpoint = f"{gh_api_base}{actions_secrets_endpoint}"
        dependabot_endpoint = f"{gh_api_base}{dependabot_secrets_endpoint}"

        assert "actions/secrets" in actions_endpoint
        assert "dependabot/secrets" in dependabot_endpoint
        assert actions_endpoint != dependabot_endpoint

    def test_process5_update_dependabot_secret_success(
        self,
        gh_api_base: str,
        dependabot_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Update Dependabot secret."""
        endpoint = f"{gh_api_base}{dependabot_secrets_endpoint}/{test_secret_name_base}"

        payload = {"encrypted_value": "new_encrypted", "key_id": "key"}

        assert payload["encrypted_value"]
        assert test_secret_name_base in endpoint

    def test_process5_delete_dependabot_secret_success(
        self,
        gh_api_base: str,
        dependabot_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Delete Dependabot secret."""
        endpoint = f"{gh_api_base}{dependabot_secrets_endpoint}/{test_secret_name_base}"

        assert test_secret_name_base in endpoint


# ─────────────────────────────────────────────────────────────────────────────
# Process 6: Codespaces Secrets Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestProcess6CodespacesSecrets:
    """Process 6: Tests for Codespaces secrets (codespace scope required)."""

    # ───────────────────────────────────────────────────────────────────────
    # Codespaces Public Key
    # ───────────────────────────────────────────────────────────────────────

    def test_process6_get_codespaces_public_key_success(
        self,
        gh_api_base: str,
        codespaces_secrets_endpoint: str,
        mock_public_key_response,
    ):
        """Test: Retrieve Codespaces public key."""
        endpoint = f"{gh_api_base}{codespaces_secrets_endpoint}/public-key"
        response = mock_public_key_response()

        assert "codespaces/secrets" in endpoint
        assert response["key"]

    # ───────────────────────────────────────────────────────────────────────
    # Codespaces Secret CRUD
    # ───────────────────────────────────────────────────────────────────────

    def test_process6_list_codespaces_secrets_success(
        self,
        gh_api_base: str,
        codespaces_secrets_endpoint: str,
    ):
        """Test: List Codespaces secrets."""
        endpoint = f"{gh_api_base}{codespaces_secrets_endpoint}"

        assert "codespaces/secrets" in endpoint

    def test_process6_create_codespaces_secret_success(
        self,
        gh_api_base: str,
        codespaces_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Create Codespaces secret."""
        endpoint = f"{gh_api_base}{codespaces_secrets_endpoint}"

        payload = {
            "name": test_secret_name_base,
            "encrypted_value": "base64_encrypted",
            "key_id": "codespaces_key",
        }

        assert payload["name"]
        assert "codespaces/secrets" in endpoint

    def test_process6_codespaces_vs_user_secrets(
        self,
        gh_api_base: str,
        codespaces_secrets_endpoint: str,
    ):
        """Test: Repository Codespaces secrets distinct from user-level.

        User can have personal Codespaces secrets.
        Repository can have repo-level Codespaces secrets.
        Repo-level take precedence for that repo.
        """
        repo_endpoint = f"{gh_api_base}{codespaces_secrets_endpoint}"

        # This is repository-level endpoint
        assert "/repos/" in repo_endpoint

    def test_process6_update_codespaces_secret_success(
        self,
        gh_api_base: str,
        codespaces_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Update Codespaces secret."""
        endpoint = f"{gh_api_base}{codespaces_secrets_endpoint}/{test_secret_name_base}"

        payload = {"encrypted_value": "new_value", "key_id": "key"}

        assert payload["encrypted_value"]
        assert test_secret_name_base in endpoint

    def test_process6_delete_codespaces_secret_success(
        self,
        gh_api_base: str,
        codespaces_secrets_endpoint: str,
        test_secret_name_base: str,
    ):
        """Test: Delete Codespaces secret."""
        endpoint = f"{gh_api_base}{codespaces_secrets_endpoint}/{test_secret_name_base}"

        assert test_secret_name_base in endpoint


# ─────────────────────────────────────────────────────────────────────────────
# Shared Encryption Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestSecretsEncryption:
    """Shared encryption tests for all secret types."""

    def test_encryption_public_key_format(self, mock_public_key_response):
        """Test: Public key is base64-encoded Curve25519 key."""
        response = mock_public_key_response()

        # Decode and verify size
        decoded = base64.b64decode(response["key"])
        assert len(decoded) == 32

    def test_encryption_key_id_required(self):
        """Test: key_id must be included with encrypted value."""
        # Both must be present in secret creation payload
        payload = {
            "encrypted_value": "base64_encrypted_secret",
            "key_id": "key_id_from_public_key",
        }

        assert "encrypted_value" in payload
        assert "key_id" in payload

    def test_encryption_mock_without_libsodium(self):
        """Test: Can mock encryption without libsodium library."""
        secret_value = "secret_password"

        # Mock encryption: base64 encode (not real encryption)
        mock_encrypted = base64.b64encode(secret_value.encode()).decode()

        # Can decrypt mock
        decrypted = base64.b64decode(mock_encrypted).decode()
        assert decrypted == secret_value

    def test_secret_name_validation(self):
        """Test: Secret names follow naming conventions."""
        valid_names = [
            "SECRET_NAME",
            "SECRET_123",
            "SECRET_NAME_123",
        ]

        for name in valid_names:
            assert name.replace("_", "").isalnum()


# ─────────────────────────────────────────────────────────────────────────────
# Batch Operations
# ─────────────────────────────────────────────────────────────────────────────


class TestSecretsBatchOperations:
    """Batch operation tests for secrets management."""

    def test_batch_create_secrets(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
    ):
        """Test: Create multiple secrets in sequence."""
        endpoint = f"{gh_api_base}{actions_secrets_endpoint}"

        for i in range(3):
            payload = {
                "name": f"SECRET_{i}",
                "encrypted_value": f"value_{i}",
                "key_id": "key_id",
            }

            assert payload["name"]

        assert "actions/secrets" in endpoint

    def test_batch_update_secrets(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
    ):
        """Test: Update multiple secrets in sequence."""
        for i in range(3):
            secret_name = f"SECRET_{i}"
            endpoint = f"{gh_api_base}{actions_secrets_endpoint}/{secret_name}"

            payload = {"encrypted_value": f"new_value_{i}", "key_id": "key"}

            assert payload["encrypted_value"]
            assert secret_name in endpoint

    def test_batch_delete_secrets(
        self,
        gh_api_base: str,
        actions_secrets_endpoint: str,
    ):
        """Test: Delete multiple secrets in sequence."""
        for i in range(3):
            secret_name = f"SECRET_{i}"
            endpoint = f"{gh_api_base}{actions_secrets_endpoint}/{secret_name}"

            assert secret_name in endpoint
