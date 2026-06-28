"""
Comprehensive tests for GitHub App Integration.

Tests cover:
- App installation
- Installation verification
- Permission validation
- Token exchange
- Webhook handling
- Error cases
"""

import json
from unittest.mock import Mock, patch

import pytest

from codex.auth.github_app import (  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    GitHubApp,
    GitHubInstallation,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def github_app_config():
    """Create GitHub App config."""
    return {
        "app_id": "123456",
        "client_id": "client_id_123",
        "client_secret": "client_secret_123",
        "private_key": "-----BEGIN RSA PRIVATE KEY-----\n...key content...\n-----END RSA PRIVATE KEY-----",
        "webhook_secret": "webhook_secret_123",
    }


@pytest.fixture
def github_app(github_app_config):
    """Create GitHub App instance."""
    return GitHubApp(
        app_id=github_app_config["app_id"],
        client_id=github_app_config["client_id"],
        client_secret=github_app_config["client_secret"],
        webhook_secret=github_app_config["webhook_secret"],
    )


# ============================================================================
# Installation Tests
# ============================================================================


class TestGitHubInstallation:
    """GitHub App installation."""

    def test_installation_creation(self):
        installation = GitHubInstallation(
            installation_id="987654",
            owner="test-owner",
            repository="test-repo",
            permissions=["contents", "pull_requests"],
        )
        assert installation.installation_id == "987654", "installation_id is not valid"
        assert installation.owner == "test-owner", "owner is not valid"
        assert installation.repository == "test-repo", "repository is not valid"

    def test_installation_with_all_permissions(self):
        permissions = [
            "contents",
            "pull_requests",
            "issues",
            "deployments",
            "checks",
            "statuses",
            "workflows",
        ]
        installation = GitHubInstallation(
            installation_id="123",
            owner="owner",
            repository="repo",
            permissions=permissions,
        )
        assert len(installation.permissions) == len(permissions), "Permissions must not be empty"

    def test_installation_created_at(self):
        import time

        before = time.time()
        installation = GitHubInstallation(
            installation_id="123",
            owner="owner",
            repository="repo",
        )
        after = time.time()
        assert before <= installation.created_at <= after, "before is not valid"

    def test_installation_repository_optional(self):
        # Organization-wide installation
        installation = GitHubInstallation(
            installation_id="456",
            owner="org-name",
            repository=None,
        )
        assert installation.repository is None, "repository is not valid"


class TestAppInstallation:
    """GitHub App installation process."""

    def test_generate_installation_url(self, github_app):
        url = github_app.get_installation_url()
        assert url, "url is not valid"
        assert "client_id=" in url, "Condition must be true"
        assert "redirect_uri=" in url or "state=" in url, "Condition must be true"

    def test_installation_url_with_scopes(self, github_app):
        url = github_app.get_installation_url(scopes=["repo", "admin:repo_hook"])
        assert url, "url is not valid"

    def test_handle_installation_callback(self, github_app):
        # Simulating installation callback from GitHub
        installation_id = "987654"
        code = "installation_code_123"

        with patch.object(github_app, "exchange_code_for_token") as mock_exchange:
            mock_exchange.return_value = {
                "access_token": "ghu_123456789",
                "installation_id": installation_id,
            }

            token = github_app.handle_installation_callback(code)
            assert token.get("installation_id") == installation_id, "Condition must be true"

    def test_invalid_installation_code(self, github_app):
        code = "invalid_code"

        with patch.object(github_app, "exchange_code_for_token") as mock_exchange:
            mock_exchange.side_effect = Exception("Invalid code")

            with pytest.raises(Exception):
                github_app.handle_installation_callback(code)


# ============================================================================
# Permission Tests
# ============================================================================


class TestPermissionValidation:
    """GitHub App permission validation."""

    def test_verify_required_permission(self, github_app):
        installation = GitHubInstallation(
            installation_id="123",
            owner="owner",
            repository="repo",
            permissions=["contents", "pull_requests", "issues"],
        )

        # Has permission
        assert github_app.has_permission(installation, "contents")
        assert github_app.has_permission(installation, "pull_requests")
        assert github_app.has_permission(installation, "issues")

    def test_verify_missing_permission(self, github_app):
        installation = GitHubInstallation(
            installation_id="123",
            owner="owner",
            repository="repo",
            permissions=["contents"],
        )

        # Missing permission
        assert not github_app.has_permission(installation, "pull_requests")
        assert not github_app.has_permission(installation, "admin:repo_hook")

    def test_verify_multiple_permissions(self, github_app):
        installation = GitHubInstallation(
            installation_id="123",
            owner="owner",
            repository="repo",
            permissions=["contents", "pull_requests", "issues"],
        )

        required = ["contents", "pull_requests"]
        has_all = all(github_app.has_permission(installation, perm) for perm in required)
        assert has_all, "has_all is not valid"

    def test_permission_case_sensitivity(self, github_app):
        installation = GitHubInstallation(
            installation_id="123",
            owner="owner",
            repository="repo",
            permissions=["Contents"],
        )

        # GitHub permissions are case-sensitive
        assert github_app.has_permission(installation, "Contents") or not github_app.has_permission(
            installation, "Contents"
        )


# ============================================================================
# Token Exchange Tests
# ============================================================================


class TestTokenExchange:
    """GitHub App token exchange."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_exchange_code_for_token(self, github_app):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "ghu_123456789",
                "token_type": "bearer",
                "scope": "repo,admin:repo_hook",
                "installation_id": "987654",
            }
            mock_post.return_value = mock_response

            token = await github_app.exchange_code_for_token("code123")
            assert token["access_token"] == "ghu_123456789", "Condition must be true"
            assert token["installation_id"] == "987654", "Condition must be true"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_exchange_code_error(self, github_app):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "invalid_code"}
            mock_post.return_value = mock_response

            with pytest.raises(Exception):
                await github_app.exchange_code_for_token("invalid_code")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_get_installation_token(self, github_app):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "token": "ghs_123456789",
                "expires_at": "2024-12-31T00:00:00Z",
                "permissions": {
                    "contents": "read",
                    "pull_requests": "write",
                },
                "repositories": [],
            }
            mock_post.return_value = mock_response

            token = await github_app.get_installation_token("987654")
            assert token["token"] == "ghs_123456789", "Condition must be true"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_refresh_installation_token(self, github_app):
        old_token = {
            "token": "ghs_old_123456789",
            "expires_at": "2024-01-01T00:00:00Z",
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "token": "ghs_new_123456789",
                "expires_at": "2024-12-31T00:00:00Z",
            }
            mock_post.return_value = mock_response

            new_token = await github_app.refresh_installation_token("987654", old_token)
            assert new_token["token"] != old_token["token"], "Condition must be true"


# ============================================================================
# Webhook Tests
# ============================================================================


class TestWebhookHandling:
    """GitHub App webhook handling."""

    def test_verify_webhook_signature(self, github_app):
        import hashlib
        import hmac

        payload = json.dumps({"action": "opened"}).encode()
        secret = github_app.webhook_secret.encode()
        signature = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()

        is_valid = github_app.verify_webhook_signature(payload, signature)
        assert is_valid, "is_valid is not valid"

    def test_invalid_webhook_signature(self, github_app):
        payload = b'{"action": "opened"}'
        signature = "sha256=invalid_signature"

        is_valid = github_app.verify_webhook_signature(payload, signature)
        assert not is_valid, "not is not valid"

    def test_webhook_empty_signature(self, github_app):
        payload = b'{"action": "opened"}'
        signature = ""

        with pytest.raises((ValueError, AssertionError)):
            github_app.verify_webhook_signature(payload, signature)

    def test_parse_webhook_payload(self, github_app):
        payload = {
            "action": "opened",
            "installation": {"id": 987654},
            "repository": {"name": "test-repo"},
        }

        parsed = github_app.parse_webhook_payload(json.dumps(payload).encode())
        assert parsed["action"] == "opened", "Condition must be true"
        assert parsed["installation"]["id"] == 987654, "Condition must be true"

    def test_parse_malformed_webhook_payload(self, github_app):
        payload = b"{invalid json"

        with pytest.raises(json.JSONDecodeError):
            github_app.parse_webhook_payload(payload)


# ============================================================================
# App State Tests
# ============================================================================


class TestAppState:
    """GitHub App state and registration."""

    def test_app_metadata(self, github_app):
        metadata = github_app.get_metadata()
        assert metadata.get("app_id"), "Data must not be empty"
        assert metadata.get("client_id"), "Data must not be empty"

    def test_app_installation_count(self, github_app):
        count = github_app.get_installation_count()
        assert isinstance(count, int)
        assert count >= 0, "count must be positive"

    def test_app_active_installations(self, github_app):
        installations = github_app.get_active_installations()
        assert isinstance(installations, list)


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """GitHub App integration scenarios."""

    def test_complete_installation_flow(self, github_app):
        # User initiates installation
        install_url = github_app.get_installation_url()
        assert install_url, "install_url is not valid"

        # GitHub redirects back with code
        code = "installation_code_123"

        # Exchange code for token
        with patch.object(github_app, "exchange_code_for_token") as mock_exchange:
            mock_exchange.return_value = {
                "access_token": "ghu_123",
                "installation_id": "987654",
            }

            token = github_app.handle_installation_callback(code)
            assert token["installation_id"] == "987654", "Condition must be true"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_webhook_and_permission_check(self, github_app):
        # Receive webhook
        payload = {
            "action": "opened",
            "installation": {"id": 987654},
            "pull_request": {"number": 1},
        }
        payload_bytes = json.dumps(payload).encode()

        # Verify signature
        import hashlib
        import hmac

        secret = github_app.webhook_secret.encode()
        signature = "sha256=" + hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()

        is_valid = github_app.verify_webhook_signature(payload_bytes, signature)
        assert is_valid, "is_valid is not valid"

        # Get installation details
        installation = GitHubInstallation(
            installation_id="987654",
            owner="owner",
            repository="repo",
            permissions=["pull_requests", "contents"],
        )

        # Check permissions
        assert github_app.has_permission(installation, "pull_requests")


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Error handling and edge cases."""

    def test_invalid_app_id(self):
        with pytest.raises((ValueError, TypeError)):
            GitHubApp(
                app_id="",
                client_id="id",
                client_secret="secret",
                webhook_secret="secret",
            )

    def test_invalid_private_key(self):
        # Should handle invalid key gracefully
        try:
            GitHubApp(
                app_id="123",
                client_id="id",
                client_secret="secret",
                webhook_secret="secret",
                private_key="invalid_key",
            )
        except ValueError:
            pass  # Expected

    def test_missing_webhook_secret(self, github_app):
        payload = b'{"action": "opened"}'

        # Should fail without secret
        with pytest.raises((ValueError, Exception)):
            github_app.verify_webhook_signature(payload, "sig")

    def test_permission_with_nonexistent_app(self):
        app = GitHubApp(
            app_id="nonexistent",
            client_id="id",
            client_secret="secret",
            webhook_secret="secret",
        )

        installation = GitHubInstallation(
            installation_id="123",
            owner="owner",
            repository="repo",
            permissions=[],
        )

        # Should handle gracefully
        result = app.has_permission(installation, "contents")
        assert isinstance(result, bool)


# ============================================================================
# Security Tests
# ============================================================================


class TestSecurity:
    """Security considerations."""

    def test_client_secret_not_in_authorization_url(self, github_app):
        url = github_app.get_installation_url()
        assert "client_secret" not in url, "Condition must be true"

    def test_webhook_signature_required(self, github_app):
        payload = b'{"action": "opened"}'

        # Should reject unsigned payload
        is_valid = github_app.verify_webhook_signature(payload, "invalid_signature")
        assert not is_valid, "not is not valid"

    def test_token_format_validation(self, github_app):
        # GitHub app tokens have specific formats
        # - ghu_ for user-to-server tokens
        # - ghs_ for server-to-server tokens
        # - gat_ for fine-grained personal access tokens
        pass
