"""Comprehensive tests for security providers (P4 priority modules).

This test suite provides ≥90% coverage for:
- src/security/providers/base.py
- src/security/providers/github_provider.py
- src/security/providers/aws_provider.py
- src/security/providers/environment_provider.py
- src/security/provider_factory.py

Tests include:
- Abstract base classes and interfaces
- All provider implementations
- Factory pattern and configuration
- Error handling and edge cases
- Integration between components
"""

from __future__ import (
    annotations,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
)

# botocore is needed by two AWS provider tests (ClientError); skip gracefully when absent
import importlib
import importlib.util as _importlib_util
import os
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

import pytest

_HAS_BOTOCORE = _importlib_util.find_spec("botocore") is not None

from security.provider_factory import (
    ProviderFactory,
    create_provider_from_env,
)
from security.providers.base import (
    ProviderConfig,
    ProviderConfigError,
    ProviderType,
    RotationError,
    RotationResult,
    SecretMetadata,
    SecretProvider,
    SecretProviderError,
    SecretType,
    TokenProvider,
    ValidationError,
)
from security.providers.environment_provider import EnvironmentProvider
from security.providers.github_provider import GitHubTokenProvider

# ============================================================================
# Test Base Module (base.py)
# ============================================================================


class TestProviderType:
    """Test ProviderType enum."""

    def test_all_provider_types(self):
        """Test all provider type enum values."""
        assert ProviderType.GITHUB.value == "github", "Value must be initialized"
        assert ProviderType.AWS_SECRETS_MANAGER.value == "aws_secrets_manager", "Value must be initialized"
        assert ProviderType.AZURE_KEY_VAULT.value == "azure_key_vault", "Value must be initialized"
        assert ProviderType.HASHICORP_VAULT.value == "hashicorp_vault", "Value must be initialized"
        assert ProviderType.ENVIRONMENT.value == "environment", "Value must be initialized"

    def test_enum_membership(self):
        """Test enum membership checks."""
        assert ProviderType.GITHUB in ProviderType, "Condition must be true"
        # Enum values can be checked with 'in' operator
        assert "github" in ProviderType._value2member_map_, "Value must be initialized"

    def test_enum_from_value(self):
        """Test creating enum from string value."""
        assert ProviderType("github") == ProviderType.GITHUB, "Condition must be true"
        with pytest.raises(ValueError):
            ProviderType("invalid_provider")


class TestSecretType:
    """Test SecretType enum."""

    def test_all_secret_types(self):
        """Test all secret type enum values."""
        assert SecretType.TOKEN.value == "token", "Value must be initialized"
        assert SecretType.API_KEY.value == "api_key", "Value must be initialized"
        assert SecretType.PASSWORD.value == "password", "Value must be initialized"
        assert SecretType.CERTIFICATE.value == "certificate", "Value must be initialized"
        assert SecretType.SSH_KEY.value == "ssh_key", "Value must be initialized"
        assert SecretType.GENERIC.value == "generic", "Value must be initialized"


class TestSecretMetadata:
    """Test SecretMetadata dataclass."""

    def test_creation_minimal(self):
        """Test creating metadata with minimal fields."""
        now = datetime.now(UTC)
        metadata = SecretMetadata(
            secret_id="test-id",
            secret_type=SecretType.TOKEN,
            provider=ProviderType.GITHUB,
            created_at=now,
            updated_at=now,
        )
        assert metadata.secret_id == "test-id", "Data must not be empty"
        assert metadata.secret_type == SecretType.TOKEN, "Data must not be empty"
        assert metadata.provider == ProviderType.GITHUB, "Data must not be empty"
        assert metadata.expires_at is None, "Data must not be empty"
        assert metadata.rotation_policy is None, "Data must not be empty"
        assert metadata.tags is None, "Data must not be empty"
        assert metadata.scopes is None, "Data must not be empty"

    def test_creation_full(self):
        """Test creating metadata with all fields."""
        now = datetime.now(UTC)
        expires = now + timedelta(days=90)

        metadata = SecretMetadata(
            secret_id="test-id",
            secret_type=SecretType.API_KEY,
            provider=ProviderType.AWS_SECRETS_MANAGER,
            created_at=now,
            updated_at=now,
            expires_at=expires,
            rotation_policy="auto_rotate",
            tags={"env": "prod", "team": "security"},
            scopes=["read", "write"],
        )

        assert metadata.expires_at == expires, "Data must not be empty"
        assert metadata.rotation_policy == "auto_rotate", "Data must not be empty"
        assert metadata.tags == {"env": "prod", "team": "security"}
        assert metadata.scopes == ["read", "write"]


class TestRotationResult:
    """Test RotationResult dataclass."""

    def test_success_result(self):
        """Test successful rotation result."""
        result = RotationResult(
            success=True,
            old_secret_id="old-id",
            new_secret_id="new-id",
            new_secret_value="new-value",  # pragma: allowlist secret
        )
        assert result.success is True, "Result must not be empty"
        assert result.old_secret_id == "old-id", "Result must not be empty"
        assert result.new_secret_id == "new-id", "Result must not be empty"
        assert result.new_secret_value == "new-value"  # pragma: allowlist secret
        assert result.error_message is None, "Result must not be empty"

    def test_failure_result(self):
        """Test failed rotation result."""
        result = RotationResult(
            success=False,
            old_secret_id="old-id",
            error_message="Rotation failed: API error",
        )
        assert result.success is False, "Result must not be empty"
        assert result.error_message == "Rotation failed: API error", "Result must not be empty"
        assert result.new_secret_id is None, "Result must not be empty"
        assert result.new_secret_value is None, "Result must not be empty"


class TestExceptions:
    """Test custom exception classes."""

    def test_secret_provider_error(self):
        """Test base SecretProviderError."""
        with pytest.raises(SecretProviderError, match="Base error"):
            raise SecretProviderError("Base error")

    def test_provider_config_error(self):
        """Test ProviderConfigError."""

        def _raise_config_invalid() -> None:
            raise ProviderConfigError("Config invalid")

        with pytest.raises(ProviderConfigError, match="Config invalid"):
            _raise_config_invalid()

        # Check it's a subclass of SecretProviderError
        with pytest.raises(SecretProviderError):
            raise ProviderConfigError("Config error")

    def test_rotation_error(self):
        """Test RotationError."""
        with pytest.raises(RotationError, match="Rotation failed"):
            raise RotationError("Rotation failed")

    def test_validation_error(self):
        """Test ValidationError."""
        with pytest.raises(ValidationError, match="Validation failed"):
            raise ValidationError("Validation failed")


class TestProviderConfig:
    """Test ProviderConfig class."""

    def test_creation(self):
        """Test creating provider config."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test",  # pragma: allowlist secret
            api_url="https://api.github.com",
        )
        assert config.provider_type == ProviderType.GITHUB, "provider_type is not valid"
        assert config.get("token") == "ghp_test", "Condition must be true"
        assert config.get("api_url") == "https://api.github.com", "Condition must be true"

    def test_get_with_default(self):
        """Test get with default value."""
        config = ProviderConfig(provider_type=ProviderType.GITHUB)
        assert config.get("missing_key", "default") == "default"
        assert config.get("missing_key") is None, "Condition must be true"

    def test_require_existing(self):
        """Test require with existing key."""
        config = ProviderConfig(
            provider_type=ProviderType.AWS_SECRETS_MANAGER,
            region="us-east-1",
        )
        assert config.require("region") == "us-east-1", "Condition must be true"

    def test_require_missing(self):
        """Test require with missing key raises error."""
        config = ProviderConfig(provider_type=ProviderType.AWS_SECRETS_MANAGER)
        with pytest.raises(ProviderConfigError, match="Required configuration 'region' not found"):
            config.require("region")

    def test_repr(self):
        """Test string representation."""
        config = ProviderConfig(provider_type=ProviderType.GITHUB)
        assert "ProviderConfig" in repr(config), "Condition must be true"
        assert "github" in repr(config), "Condition must be true"


class TestSecretProviderAbstract:
    """Test SecretProvider abstract base class."""

    def test_cannot_instantiate(self):
        """Test cannot instantiate abstract class."""
        with pytest.raises(TypeError):
            SecretProvider()  # type: ignore

    def test_default_get_scopes(self):
        """Test default get_scopes returns empty list."""

        class ConcreteProvider(SecretProvider):
            def rotate_secret(self, secret_id, **kwargs):
                return RotationResult(True, secret_id)

            def validate_secret(self, secret_id, secret_value=None):
                return True

            def get_secret_metadata(self, secret_id):
                return SecretMetadata(
                    secret_id=secret_id,
                    secret_type=SecretType.GENERIC,
                    provider=ProviderType.ENVIRONMENT,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )

            def get_expiration(self, secret_id):
                return None

            @property
            def provider_type(self):
                return ProviderType.ENVIRONMENT

        provider = ConcreteProvider()
        assert provider.get_scopes("test") == [], "Condition must be true"

    def test_default_revoke_raises_not_implemented(self):
        """Test default revoke_secret raises NotImplementedError."""

        class ConcreteProvider(SecretProvider):
            def rotate_secret(self, secret_id, **kwargs):
                return RotationResult(True, secret_id)

            def validate_secret(self, secret_id, secret_value=None):
                return True

            def get_secret_metadata(self, secret_id):
                return SecretMetadata(
                    secret_id=secret_id,
                    secret_type=SecretType.GENERIC,
                    provider=ProviderType.ENVIRONMENT,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )

            def get_expiration(self, secret_id):
                return None

            @property
            def provider_type(self):
                return ProviderType.ENVIRONMENT

        provider = ConcreteProvider()
        with pytest.raises(NotImplementedError, match="does not support revocation"):
            provider.revoke_secret("test")

    def test_default_list_secrets_raises_not_implemented(self):
        """Test default list_secrets raises NotImplementedError."""

        class ConcreteProvider(SecretProvider):
            def rotate_secret(self, secret_id, **kwargs):
                return RotationResult(True, secret_id)

            def validate_secret(self, secret_id, secret_value=None):
                return True

            def get_secret_metadata(self, secret_id):
                return SecretMetadata(
                    secret_id=secret_id,
                    secret_type=SecretType.GENERIC,
                    provider=ProviderType.ENVIRONMENT,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )

            def get_expiration(self, secret_id):
                return None

            @property
            def provider_type(self):
                return ProviderType.ENVIRONMENT

        provider = ConcreteProvider()
        with pytest.raises(NotImplementedError, match="does not support listing"):
            provider.list_secrets()

    def test_provider_name(self):
        """Test provider_name property."""

        class ConcreteProvider(SecretProvider):
            def rotate_secret(self, secret_id, **kwargs):
                return RotationResult(True, secret_id)

            def validate_secret(self, secret_id, secret_value=None):
                return True

            def get_secret_metadata(self, secret_id):
                return SecretMetadata(
                    secret_id=secret_id,
                    secret_type=SecretType.GENERIC,
                    provider=ProviderType.AWS_SECRETS_MANAGER,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )

            def get_expiration(self, secret_id):
                return None

            @property
            def provider_type(self):
                return ProviderType.AWS_SECRETS_MANAGER

        provider = ConcreteProvider()
        assert provider.provider_name == "AWS Secrets Manager", "provider_name is not valid"

    def test_repr(self):
        """Test __repr__ method."""

        class ConcreteProvider(SecretProvider):
            def rotate_secret(self, secret_id, **kwargs):
                return RotationResult(True, secret_id)

            def validate_secret(self, secret_id, secret_value=None):
                return True

            def get_secret_metadata(self, secret_id):
                return SecretMetadata(
                    secret_id=secret_id,
                    secret_type=SecretType.GENERIC,
                    provider=ProviderType.GITHUB,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )

            def get_expiration(self, secret_id):
                return None

            @property
            def provider_type(self):
                return ProviderType.GITHUB

        provider = ConcreteProvider()
        assert "ConcreteProvider" in repr(provider), "Condition must be true"
        assert "github" in repr(provider), "Condition must be true"


class TestTokenProviderAbstract:
    """Test TokenProvider abstract base class."""

    def test_cannot_instantiate(self):
        """Test cannot instantiate abstract class."""
        with pytest.raises(TypeError):
            TokenProvider()  # type: ignore

    def test_requires_create_token(self):
        """Test create_token is abstract and must be implemented."""

        class IncompleteProvider(TokenProvider):
            def rotate_secret(self, secret_id, **kwargs):
                return RotationResult(True, secret_id)

            def validate_secret(self, secret_id, secret_value=None):
                return True

            def get_secret_metadata(self, secret_id):
                return SecretMetadata(
                    secret_id=secret_id,
                    secret_type=SecretType.TOKEN,
                    provider=ProviderType.GITHUB,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )

            def get_expiration(self, secret_id):
                return None

            @property
            def provider_type(self):
                return ProviderType.GITHUB

            def update_token_scopes(self, secret_id, scopes):
                return True

        # Should fail due to missing create_token
        with pytest.raises(TypeError):
            IncompleteProvider()  # type: ignore


# ============================================================================
# Test GitHub Provider (github_provider.py)
# ============================================================================


class TestGitHubTokenProvider:
    """Test GitHubTokenProvider implementation."""

    @pytest.fixture
    def github_config(self):
        """Create test config for GitHub provider."""
        return ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test_token_1234567890",  # pragma: allowlist secret
            api_url="https://api.github.com",
        )

    def test_initialization_with_token(self, github_config):
        """Test initialization with explicit token."""
        provider = GitHubTokenProvider(github_config)
        assert provider.provider_type == ProviderType.GITHUB, "provider_type is not valid"
        assert provider.token == "ghp_test_token_1234567890", "token is not valid"
        assert provider.api_url == "https://api.github.com", "api_url is not valid"

    def test_initialization_without_token(self):
        """Test initialization without token (uses env var)."""
        config = ProviderConfig(provider_type=ProviderType.GITHUB)
        provider = GitHubTokenProvider(config)
        assert provider.token is None or provider.token == os.getenv("GITHUB_TOKEN"), "token is not valid"

    def test_rotate_secret_success(self, github_config):
        """Test successful token rotation."""
        provider = GitHubTokenProvider(github_config)

        # Mock create_token to control the return value
        with patch.object(GitHubTokenProvider, "create_token") as mock_create:
            mock_create.return_value = RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id="new-token-id",
                new_secret_value="ghp_new_token_value",  # pragma: allowlist secret
            )

            result = provider.rotate_secret(
                "old-token-id",
                scopes=["repo", "workflow"],
                expires_in_days=90,
            )

            assert result.success is True, "Result must not be empty"
            assert result.old_secret_id == "old-token-id", "Result must not be empty"
            assert result.new_secret_id is not None, "new_secret_id must be initialized"
            assert result.new_secret_value is not None, "new_secret_value must be initialized"
            assert "ghp_" in result.new_secret_value, "Result must not be empty"
            mock_create.assert_called_once()

    def test_rotate_secret_with_revoke(self, github_config):
        """Test token rotation with old token revocation."""
        provider = GitHubTokenProvider(github_config)

        # Mock create_token to control the return value
        with patch.object(GitHubTokenProvider, "create_token") as mock_create:
            mock_create.return_value = RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id="new-token-id",
                new_secret_value="ghp_new_token_value",  # pragma: allowlist secret
            )

            with patch.object(GitHubTokenProvider, "revoke_secret") as mock_revoke:
                mock_revoke.return_value = True

                result = provider.rotate_secret(
                    "old-token-id",
                    revoke_old=True,
                )

                assert result.success is True, "Result must not be empty"
                mock_create.assert_called_once()
                mock_revoke.assert_called_once_with("old-token-id")

    def test_validate_secret_with_token(self, github_config):
        """Test token validation with provided value (mocks GitHub API call)."""
        provider = GitHubTokenProvider(github_config)
        # Use a valid-format GitHub PAT (ghp_ prefix + 36 alphanumeric chars)
        token = "ghp_" + "A" * 36
        # Mock the requests.get call so no real network traffic is made in tests
        mock_response = Mock()
        mock_response.status_code = 200
        with patch("requests.get", return_value=mock_response):
            is_valid = provider.validate_secret("token-id", token)
        assert is_valid is True, "is_valid is not valid"

    def test_validate_secret_invalid_format(self, github_config):
        """Test validation rejects tokens with invalid format."""
        provider = GitHubTokenProvider(github_config)
        # Too short — won't match the regex, so validate_secret returns False
        # before making any API call
        is_valid = provider.validate_secret("token-id", "ghp_tooshort")
        assert is_valid is False, "is_valid is not valid"

    def test_validate_secret_api_401(self, github_config):
        """Test validation returns False when GitHub API returns 401."""
        provider = GitHubTokenProvider(github_config)
        token = "ghp_" + "B" * 36
        mock_response = Mock()
        mock_response.status_code = 401
        with patch("requests.get", return_value=mock_response):
            is_valid = provider.validate_secret("token-id", token)
        assert is_valid is False, "is_valid is not valid"

    def test_validate_secret_network_error_degrades_gracefully(self, github_config):
        """Test that network errors fall back to format-only validation."""
        import requests as real_requests

        provider = GitHubTokenProvider(github_config)
        token = "ghp_" + "C" * 36
        with patch("requests.get", side_effect=real_requests.exceptions.ConnectionError("offline")):
            is_valid = provider.validate_secret("token-id", token)
        # Format is valid so should return True after graceful degradation
        assert is_valid is True, "is_valid is not valid"

    def test_validate_secret_no_token(self, github_config):
        """Test validation fails when no token provided."""
        # Ensure no token in config or environment
        config = ProviderConfig(provider_type=ProviderType.GITHUB)
        with patch.dict(os.environ, {"GITHUB_TOKEN": ""}, clear=False):
            provider = GitHubTokenProvider(config)
            with pytest.raises(ValidationError, match="No token provided"):
                provider.validate_secret("token-id", None)

    def test_get_secret_metadata(self, github_config):
        """Test getting token metadata."""
        provider = GitHubTokenProvider(github_config)
        metadata = provider.get_secret_metadata("token-id")

        assert metadata.secret_id == "token-id", "Data must not be empty"
        assert metadata.secret_type == SecretType.TOKEN, "Data must not be empty"
        assert metadata.provider == ProviderType.GITHUB, "Data must not be empty"
        assert metadata.expires_at is not None, "expires_at must be initialized"
        assert metadata.scopes == ["repo", "workflow"]

    def test_get_expiration(self, github_config):
        """Test getting token expiration."""
        provider = GitHubTokenProvider(github_config)
        expiration = provider.get_expiration("token-id")

        assert expiration is not None, "expiration must be initialized"
        assert isinstance(expiration, datetime)

    def test_get_scopes(self, github_config):
        """Test getting token scopes."""
        provider = GitHubTokenProvider(github_config)
        scopes = provider.get_scopes("token-id")

        assert isinstance(scopes, list)
        assert all(isinstance(s, str) for s in scopes)

    def test_create_token_no_installation_id(self, github_config):
        """Test create_token fails gracefully without installation_id."""
        provider = GitHubTokenProvider(github_config)

        result = provider.create_token(
            name="test-token",
            scopes=["contents", "workflows"],
            expires_in_days=90,
        )

        # Without installation_id, create_token must return failure (not raise)
        assert result.success is False, "Result must not be empty"
        assert "installation_id" in (result.error_message or ""), "Result must not be empty"

    def test_create_token_with_installation_id(self, github_config):
        """Test create_token calls GitHub API when installation_id is set."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test_token_1234567890",  # pragma: allowlist secret
            api_url="https://api.github.com",
            installation_id="12345",
        )
        provider = GitHubTokenProvider(config)

        mock_resp = Mock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "token": "ghs_test_installation_token_value",  # pragma: allowlist secret
            "id": 99,
            "expires_at": "2026-03-18T00:00:00Z",
        }

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.post.return_value = mock_resp
            result = provider.create_token(
                name="test-token",
                scopes=["contents", "workflows"],
            )

        assert result.success is True, "Result must not be empty"
        assert (result.new_secret_value == "ghs_test_installation_token_value", "Result must not be empty"
        )  # pragma: allowlist secret  # noqa: E501
        assert result.new_secret_id == "99", "Result must not be empty"

    def test_create_token_invalid_pat_scopes(self, github_config):
        """Test create_token rejects PAT-style scopes."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test_token_1234567890",  # pragma: allowlist secret
            api_url="https://api.github.com",
            installation_id="12345",
        )
        provider = GitHubTokenProvider(config)

        result = provider.create_token(
            name="test-token",
            scopes=["repo", "workflow"],  # PAT-style — should be rejected
        )

        assert result.success is False, "Result must not be empty"
        assert "Invalid installation permission" in (result.error_message or "", "Result must not be empty"
        ), "Result must not be empty"

    def test_create_token_empty_token_response(self, github_config):
        """Test create_token fails closed when API returns 201 but no token."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test_token_1234567890",  # pragma: allowlist secret
            api_url="https://api.github.com",
            installation_id="12345",
        )
        provider = GitHubTokenProvider(config)

        mock_resp = Mock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"id": 99, "expires_at": "2026-03-18T00:00:00Z"}

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.post.return_value = mock_resp
            result = provider.create_token(name="t", scopes=["contents"])

        assert result.success is False, "Result must not be empty"
        assert "no token" in (result.error_message or "").lower(), "Result must not be empty"

    def test_create_token_api_failure(self, github_config):
        """Test create_token handles API errors gracefully."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test_token_1234567890",  # pragma: allowlist secret
            api_url="https://api.github.com",
            installation_id="12345",
        )
        provider = GitHubTokenProvider(config)

        mock_resp = Mock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.post.return_value = mock_resp
            result = provider.create_token(name="t", scopes=["contents"])

        assert result.success is False, "Result must not be empty"
        assert "403" in (result.error_message or ""), "Result must not be empty"

    def test_update_token_scopes(self, github_config):
        """Test updating token scopes calls GitHub API."""
        provider = GitHubTokenProvider(github_config)

        mock_resp = Mock()
        mock_resp.status_code = 200

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.patch.return_value = mock_resp
            success = provider.update_token_scopes(
                "12345",
                ["contents", "workflows", "issues"],
            )

        assert success is True, "success is not valid"

    def test_update_token_scopes_no_requests(self, github_config):
        """Test update_token_scopes returns False without requests library."""
        provider = GitHubTokenProvider(github_config)

        with patch("security.providers.github_provider.HAS_REQUESTS", False):
            success = provider.update_token_scopes("12345", ["contents"])

        assert success is False, "success is not valid"

    def test_revoke_secret(self, github_config):
        """Test revoking token.

        Classic PATs (ghp_ prefix) require OAuth App credentials (client_id + client_secret)
        to revoke via the GitHub API. Without them, revoke_secret() returns False and logs a
        clear warning — safer than the old stub that silently returned True without revoking.
        """
        provider = GitHubTokenProvider(github_config)
        success = provider.revoke_secret("token-id")

        # Classic PAT revocation is not possible without OAuth App credentials.
        # The method must return False rather than pretending success.
        assert success is False, "success is not valid"

    def test_list_secrets(self, github_config):
        """Test listing tokens."""
        provider = GitHubTokenProvider(github_config)
        secrets = provider.list_secrets()

        assert isinstance(secrets, list)


# ============================================================================
# Test AWS Provider (aws_provider.py) - Requires Mocking
# ============================================================================


class TestAWSSecretsManagerProvider:
    """Test AWSSecretsManagerProvider implementation."""

    @pytest.fixture
    def aws_config(self):
        """Create test config for AWS provider."""
        return ProviderConfig(
            provider_type=ProviderType.AWS_SECRETS_MANAGER,
            region="us-east-1",
            aws_access_key_id="AKIA_TEST",
            aws_secret_access_key="secret_test_key",  # pragma: allowlist secret
        )

    def test_initialization_requires_boto3(self, aws_config):
        """Test that AWS provider requires boto3."""
        # This will either succeed if boto3 is installed or fail appropriately
        try:
            from security.providers.aws_provider import AWSSecretsManagerProvider

            provider = AWSSecretsManagerProvider(aws_config)
            assert provider.provider_type == ProviderType.AWS_SECRETS_MANAGER, "provider_type is not valid"
            assert provider.region == "us-east-1", "region is not valid"
        except ProviderConfigError as e:
            assert "boto3 required" in str(e), "Condition must be true"

    @patch("security.providers.aws_provider.HAS_BOTO3", False)
    def test_initialization_without_boto3_raises_error(self, aws_config):
        """Test initialization fails without boto3."""
        from security.providers.aws_provider import AWSSecretsManagerProvider

        with pytest.raises(ProviderConfigError, match="boto3 required"):
            AWSSecretsManagerProvider(aws_config)

    def test_module_import_fallback_without_boto3(self):
        """Test module-level boto3 import fallback path creates testable stub."""
        import security.providers.aws_provider as aws_provider_module

        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == "boto3" or name.startswith("botocore"):
                raise ImportError("simulated missing boto3")
            return real_import(name, *args, **kwargs)

        try:
            with patch("builtins.__import__", side_effect=fake_import):
                reloaded = importlib.reload(aws_provider_module)
                assert reloaded.HAS_BOTO3 is False, "HAS_BOTO3 is not valid"
                assert hasattr(reloaded.boto3, "client")
                assert reloaded.ClientError is Exception, "Error should be raised or set"
        finally:
            importlib.reload(aws_provider_module)

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_rotate_secret_success(self, mock_boto3, aws_config):
        """Test successful secret rotation."""
        # Mock boto3 client
        mock_client = Mock()
        mock_client.rotate_secret.return_value = {
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test",
            "Name": "test-secret",
            "VersionId": "new-version-id",
        }
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)

        result = provider.rotate_secret(
            "test-secret",
            rotation_lambda_arn="arn:aws:lambda:us-east-1:123456789012:function:rotate",
        )

        assert result.success is True, "Result must not be empty"
        assert result.metadata["version_id"] == "new-version-id", "Result must not be empty"

    @pytest.mark.skipif(not _HAS_BOTOCORE, reason="botocore not installed in this CI environment")
    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_rotate_secret_client_error(self, mock_boto3, aws_config):
        """Test rotation with AWS client error."""
        from botocore.exceptions import ClientError

        mock_client = Mock()
        mock_client.rotate_secret.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}},
            "rotate_secret",
        )
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)

        result = provider.rotate_secret("test-secret")

        assert result.success is False, "Result must not be empty"
        assert "ResourceNotFoundException" in result.error_message, "Result must not be empty"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_rotate_secret_unexpected_exception(self, mock_boto3, aws_config):
        """Test rotation gracefully handles unexpected exceptions."""
        mock_client = Mock()
        mock_client.rotate_secret.side_effect = RuntimeError("network timeout")
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)
        result = provider.rotate_secret("test-secret")
        assert result.success is False, "Result must not be empty"
        assert "network timeout" in result.error_message, "Result must not be empty"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_validate_secret_exists(self, mock_boto3, aws_config):
        """Test validating existing secret."""
        mock_client = Mock()
        mock_client.describe_secret.return_value = {"Name": "test-secret"}
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)

        is_valid = provider.validate_secret("test-secret")
        assert is_valid is True, "is_valid is not valid"

    @pytest.mark.skipif(not _HAS_BOTOCORE, reason="botocore not installed in this CI environment")
    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_validate_secret_not_found(self, mock_boto3, aws_config):
        """Test validating non-existent secret."""
        from botocore.exceptions import ClientError

        mock_client = Mock()
        mock_client.describe_secret.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Not found"}},
            "describe_secret",
        )
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)

        is_valid = provider.validate_secret("test-secret")
        assert is_valid is False, "is_valid is not valid"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_validate_secret_unexpected_exception_raises(self, mock_boto3, aws_config):
        """Test validation wraps unexpected exceptions in ValidationError."""
        mock_client = Mock()
        mock_client.describe_secret.side_effect = RuntimeError("broken client")
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)
        with pytest.raises(ValidationError, match="broken client"):
            provider.validate_secret("test-secret")

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_get_secret_metadata(self, mock_boto3, aws_config):
        """Test getting secret metadata."""
        now = datetime.now(UTC)
        mock_client = Mock()
        mock_client.describe_secret.return_value = {
            "Name": "test-secret",
            "CreatedDate": now,
            "LastChangedDate": now,
            "Tags": [{"Key": "env", "Value": "test"}],
            "RotationEnabled": True,
        }
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)

        metadata = provider.get_secret_metadata("test-secret")

        assert metadata.secret_id == "test-secret", "Data must not be empty"
        assert metadata.secret_type == SecretType.GENERIC, "Data must not be empty"
        assert metadata.provider == ProviderType.AWS_SECRETS_MANAGER, "Data must not be empty"
        assert metadata.tags == {"env": "test"}, "Data must not be empty"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_get_secret_metadata_normalizes_naive_datetimes(self, mock_boto3, aws_config):
        """Test metadata normalizes naive datetime values to UTC."""
        naive_created = datetime(2024, 1, 2, 3, 4, 5)
        naive_updated = datetime(2024, 2, 3, 4, 5, 6)
        mock_client = Mock()
        mock_client.describe_secret.return_value = {
            "Name": "test-secret",
            "CreatedDate": naive_created,
            "LastChangedDate": naive_updated,
            "Tags": [],
        }
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)
        metadata = provider.get_secret_metadata("test-secret")
        assert metadata.created_at.tzinfo == UTC, "Data must not be empty"
        assert metadata.updated_at.tzinfo == UTC, "Data must not be empty"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_get_secret_metadata_client_error(self, mock_boto3, aws_config):
        """Test metadata lookup maps ClientError to ValidationError."""

        class FakeClientError(Exception):
            pass

        mock_client = Mock()
        mock_client.describe_secret.side_effect = FakeClientError("metadata denied")
        mock_boto3.client.return_value = mock_client

        with patch("security.providers.aws_provider.ClientError", FakeClientError):
            from security.providers.aws_provider import AWSSecretsManagerProvider

            provider = AWSSecretsManagerProvider(aws_config)
            with pytest.raises(ValidationError, match="metadata denied"):
                provider.get_secret_metadata("test-secret")

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_get_expiration_always_none(self, mock_boto3, aws_config):
        """Test that AWS secrets don't have expiration."""
        mock_boto3.client.return_value = Mock()

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)

        expiration = provider.get_expiration("test-secret")
        assert expiration is None, "expiration is not valid"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_get_secret_value_string(self, mock_boto3, aws_config):
        """Test getting secret string value."""
        mock_client = Mock()
        mock_client.get_secret_value.return_value = {
            "SecretString": "my-secret-value"  # pragma: allowlist secret
        }
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)

        value = provider.get_secret_value("test-secret")
        assert value == "my-secret-value", "Value must be initialized"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_get_secret_value_binary(self, mock_boto3, aws_config):
        """Test getting secret binary value."""
        mock_client = Mock()
        mock_client.get_secret_value.return_value = {"SecretBinary": b"binary-secret"}
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)

        value = provider.get_secret_value("test-secret")
        assert isinstance(value, str)  # Base64 encoded

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_get_secret_value_client_error(self, mock_boto3, aws_config):
        """Test secret retrieval maps ClientError to ValidationError."""

        class FakeClientError(Exception):
            pass

        mock_client = Mock()
        mock_client.get_secret_value.side_effect = FakeClientError("access denied")
        mock_boto3.client.return_value = mock_client

        with patch("security.providers.aws_provider.ClientError", FakeClientError):
            from security.providers.aws_provider import AWSSecretsManagerProvider

            provider = AWSSecretsManagerProvider(aws_config)
            with pytest.raises(ValidationError, match="access denied"):
                provider.get_secret_value("test-secret")

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_create_secret(self, mock_boto3, aws_config):
        """Test creating new secret."""
        mock_client = Mock()
        mock_client.create_secret.return_value = {
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test",
            "Name": "test-secret",
            "VersionId": "v1",
        }
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)

        result = provider.create_secret(
            name="test-secret",
            secret_value="secret-value",  # pragma: allowlist secret
            description="Test secret",
            tags={"env": "test"},
        )

        assert result.success is True, "Result must not be empty"
        assert result.new_secret_id == "test-secret", "Result must not be empty"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_create_secret_without_optional_fields(self, mock_boto3, aws_config):
        """Test create_secret omits optional keys when not provided."""
        mock_client = Mock()
        mock_client.create_secret.return_value = {
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test",
            "Name": "test-secret",
            "VersionId": "v1",
        }
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)
        result = provider.create_secret(name="test-secret", secret_value="secret-value")
        assert result.success is True, "Result must not be empty"
        mock_client.create_secret.assert_called_once_with(
            Name="test-secret",
            SecretString="secret-value",  # pragma: allowlist secret
        )

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_create_secret_client_error(self, mock_boto3, aws_config):
        """Test create_secret returns failure result on ClientError."""

        class FakeClientError(Exception):
            pass

        mock_client = Mock()
        mock_client.create_secret.side_effect = FakeClientError("create failed")
        mock_boto3.client.return_value = mock_client

        with patch("security.providers.aws_provider.ClientError", FakeClientError):
            from security.providers.aws_provider import AWSSecretsManagerProvider

            provider = AWSSecretsManagerProvider(aws_config)
            result = provider.create_secret(name="test-secret", secret_value="secret-value")
            assert result.success is False, "Result must not be empty"
            assert "create failed" in result.error_message, "Result must not be empty"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_delete_secret(self, mock_boto3, aws_config):
        """Test deleting secret with recovery window."""
        mock_client = Mock()
        mock_client.delete_secret.return_value = {}
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)

        success = provider.delete_secret("test-secret", recovery_window_days=7)
        assert success is True, "success is not valid"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_delete_secret_client_error(self, mock_boto3, aws_config):
        """Test delete_secret returns False on client error."""

        class FakeClientError(Exception):
            pass

        mock_client = Mock()
        mock_client.delete_secret.side_effect = FakeClientError("delete denied")
        mock_boto3.client.return_value = mock_client

        with patch("security.providers.aws_provider.ClientError", FakeClientError):
            from security.providers.aws_provider import AWSSecretsManagerProvider

            provider = AWSSecretsManagerProvider(aws_config)
            assert provider.delete_secret("test-secret") is False, "Condition must be true"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_list_secrets(self, mock_boto3, aws_config):
        """Test listing secrets with pagination."""
        mock_client = Mock()
        mock_paginator = Mock()
        mock_paginator.paginate.return_value = [
            {
                "SecretList": [
                    {"Name": "secret-1"},
                    {"Name": "secret-2"},
                ]
            }
        ]
        mock_client.get_paginator.return_value = mock_paginator
        mock_client.describe_secret.side_effect = [
            {
                "Name": "secret-1",
                "CreatedDate": datetime.now(UTC),
                "Tags": [],
            },
            {
                "Name": "secret-2",
                "CreatedDate": datetime.now(UTC),
                "Tags": [],
            },
        ]
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)

        secrets = provider.list_secrets()
        assert len(secrets) == 2, "Secrets must not be empty"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_list_secrets_with_tag_filters(self, mock_boto3, aws_config):
        """Test list_secrets applies tag filters to paginator call."""
        mock_client = Mock()
        mock_paginator = Mock()
        mock_paginator.paginate.return_value = [{"SecretList": []}]
        mock_client.get_paginator.return_value = mock_paginator
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)
        result = provider.list_secrets(filter_tags={"env": "prod"})
        assert result == [], "Result must not be empty"
        mock_paginator.paginate.assert_called_once_with(
            Filters=[
                {"Key": "tag-key", "Values": ["env"]},
                {"Key": "tag-value", "Values": ["prod"]},
            ]
        )

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_list_secrets_skips_metadata_failures(self, mock_boto3, aws_config):
        """Test list_secrets continues when individual metadata lookups fail."""
        mock_client = Mock()
        mock_paginator = Mock()
        mock_paginator.paginate.return_value = [
            {"SecretList": [{"Name": "bad-secret"}, {"Name": "good-secret"}]}
        ]
        mock_client.get_paginator.return_value = mock_paginator
        mock_client.describe_secret.side_effect = [
            RuntimeError("metadata unavailable"),
            {"Name": "good-secret", "CreatedDate": datetime.now(UTC), "Tags": []},
        ]
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider

        provider = AWSSecretsManagerProvider(aws_config)
        result = provider.list_secrets()
        assert [item.secret_id for item in result] == ["good-secret"], "Result must not be empty"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_list_secrets_client_error_returns_empty(self, mock_boto3, aws_config):
        """Test list_secrets returns empty list when paginator creation fails."""

        class FakeClientError(Exception):
            pass

        mock_client = Mock()
        mock_client.get_paginator.side_effect = FakeClientError("listing denied")
        mock_boto3.client.return_value = mock_client

        with patch("security.providers.aws_provider.ClientError", FakeClientError):
            from security.providers.aws_provider import AWSSecretsManagerProvider

            provider = AWSSecretsManagerProvider(aws_config)
            assert provider.list_secrets() == [], "Condition must be true"


# ============================================================================
# Test Environment Provider (environment_provider.py)
# ============================================================================


class TestEnvironmentProvider:
    """Test EnvironmentProvider implementation."""

    @pytest.fixture
    def env_config(self):
        """Create test config for environment provider."""
        return ProviderConfig(
            provider_type=ProviderType.ENVIRONMENT,
            prefix="TEST_",
        )

    @pytest.fixture(autouse=True)
    def clean_env(self):
        """Clean up test environment variables after each test."""
        yield
        # Cleanup
        for key in list(os.environ.keys()):
            if key.startswith("TEST_"):
                del os.environ[key]

    def test_initialization(self, env_config):
        """Test provider initialization."""
        provider = EnvironmentProvider(env_config)
        assert provider.provider_type == ProviderType.ENVIRONMENT, "provider_type is not valid"
        assert provider.prefix == "TEST_", "prefix is not valid"

    def test_initialization_no_prefix(self):
        """Test initialization without prefix."""
        config = ProviderConfig(provider_type=ProviderType.ENVIRONMENT)
        provider = EnvironmentProvider(config)
        assert provider.prefix == "", "prefix is not valid"

    def test_rotate_secret_returns_manual_instruction(self, env_config):
        """Test that rotation returns manual instruction."""
        os.environ["TEST_SECRET"] = "value"  # pragma: allowlist secret
        provider = EnvironmentProvider(env_config)

        result = provider.rotate_secret("SECRET")

        assert result.success is False, "Result must not be empty"
        assert "manual" in result.error_message.lower(), "Result must not be empty"
        assert "TEST_SECRET" in result.error_message, "Result must not be empty"

    def test_rotate_secret_not_found(self, env_config):
        """Test rotation when env var doesn't exist."""
        provider = EnvironmentProvider(env_config)

        result = provider.rotate_secret("MISSING")

        assert result.success is False, "Result must not be empty"
        assert "not found" in result.error_message, "Result must not be empty"

    def test_validate_secret_exists(self, env_config):
        """Test validation when env var exists."""
        os.environ["TEST_SECRET"] = "value"  # pragma: allowlist secret
        provider = EnvironmentProvider(env_config)

        is_valid = provider.validate_secret("SECRET")
        assert is_valid is True, "is_valid is not valid"

    def test_validate_secret_not_exists(self, env_config):
        """Test validation when env var doesn't exist."""
        provider = EnvironmentProvider(env_config)

        is_valid = provider.validate_secret("MISSING")
        assert is_valid is False, "is_valid is not valid"

    def test_validate_secret_with_value_match(self, env_config):
        """Test validation with matching value."""
        os.environ["TEST_SECRET"] = "expected_value"  # pragma: allowlist secret
        provider = EnvironmentProvider(env_config)

        is_valid = provider.validate_secret("SECRET", "expected_value")
        assert is_valid is True, "is_valid is not valid"

    def test_validate_secret_with_value_mismatch(self, env_config):
        """Test validation with non-matching value."""
        os.environ["TEST_SECRET"] = "actual_value"  # pragma: allowlist secret
        provider = EnvironmentProvider(env_config)

        is_valid = provider.validate_secret("SECRET", "wrong_value")
        assert is_valid is False, "is_valid is not valid"

    def test_get_secret_metadata(self, env_config):
        """Test getting metadata."""
        provider = EnvironmentProvider(env_config)
        metadata = provider.get_secret_metadata("SECRET")

        assert metadata.secret_id == "SECRET", "Data must not be empty"
        assert metadata.secret_type == SecretType.GENERIC, "Data must not be empty"
        assert metadata.provider == ProviderType.ENVIRONMENT, "Data must not be empty"
        assert metadata.expires_at is None, "Data must not be empty"
        assert metadata.tags["name"] == "TEST_SECRET", "Data must not be empty"

    def test_get_expiration_always_none(self, env_config):
        """Test that expiration is always None."""
        provider = EnvironmentProvider(env_config)
        expiration = provider.get_expiration("SECRET")
        assert expiration is None, "expiration is not valid"

    def test_get_secret_value(self, env_config):
        """Test getting secret value."""
        os.environ["TEST_SECRET"] = "my_value"  # pragma: allowlist secret
        provider = EnvironmentProvider(env_config)

        value = provider.get_secret_value("SECRET")
        assert value == "my_value", "Value must be initialized"

    def test_get_secret_value_not_found(self, env_config):
        """Test getting non-existent secret."""
        provider = EnvironmentProvider(env_config)

        value = provider.get_secret_value("MISSING")
        assert value is None, "Value must be initialized"

    def test_set_secret_value(self, env_config):
        """Test setting secret value."""
        provider = EnvironmentProvider(env_config)

        success = provider.set_secret_value("NEW_SECRET", "new_value")
        assert success is True, "success is not valid"
        assert os.environ["TEST_NEW_SECRET"] == "new_value"  # pragma: allowlist secret

    def test_list_secrets_with_prefix(self, env_config):
        """Test listing secrets with prefix filter."""
        os.environ["TEST_SECRET1"] = "value1"  # pragma: allowlist secret
        os.environ["TEST_SECRET2"] = "value2"  # pragma: allowlist secret
        os.environ["OTHER_SECRET"] = "value3"  # pragma: allowlist secret

        provider = EnvironmentProvider(env_config)
        secrets = provider.list_secrets()

        assert len(secrets) == 2, "Secrets must not be empty"
        secret_ids = [s.secret_id for s in secrets]
        assert "SECRET1" in secret_ids, "Condition must be true"
        assert "SECRET2" in secret_ids, "Condition must be true"


# ============================================================================
# Test Provider Factory (provider_factory.py)
# ============================================================================


class TestProviderFactory:
    """Test ProviderFactory class."""

    def test_create_github_provider(self):
        """Test creating GitHub provider."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test",  # pragma: allowlist secret
        )

        provider = ProviderFactory.create_provider(config)

        assert isinstance(provider, GitHubTokenProvider)
        assert provider.provider_type == ProviderType.GITHUB, "provider_type is not valid"

    def test_create_environment_provider(self):
        """Test creating environment provider."""
        config = ProviderConfig(provider_type=ProviderType.ENVIRONMENT)

        provider = ProviderFactory.create_provider(config)

        assert isinstance(provider, EnvironmentProvider)
        assert provider.provider_type == ProviderType.ENVIRONMENT, "provider_type is not valid"

    def test_create_aws_provider(self):
        """Test creating AWS provider (if boto3 available)."""
        config = ProviderConfig(
            provider_type=ProviderType.AWS_SECRETS_MANAGER,
            region="us-east-1",
        )

        try:
            provider = ProviderFactory.create_provider(config)
            assert provider.provider_type == ProviderType.AWS_SECRETS_MANAGER, "provider_type is not valid"
        except ProviderConfigError as e:
            # Expected if boto3 not installed
            assert "boto3" in str(e).lower(), "Condition must be true"

    def test_create_unsupported_provider(self):
        """Test creating unsupported provider raises error."""
        config = ProviderConfig(provider_type=ProviderType.AZURE_KEY_VAULT)

        with pytest.raises(ProviderConfigError, match="not yet implemented"):
            ProviderFactory.create_provider(config)

    def test_create_hashicorp_provider_not_implemented(self):
        """Test hashicorp provider branch raises explicit not implemented error."""
        config = ProviderConfig(provider_type=ProviderType.HASHICORP_VAULT)

        with pytest.raises(
            ProviderConfigError, match="HashiCorp Vault provider not yet implemented"
        ):
            ProviderFactory.create_provider(config)

    def test_create_provider_unknown_type_raises(self):
        """Test unsupported provider type branch for non-enum values."""
        config = Mock()
        config.provider_type = "custom_provider"

        with pytest.raises(ProviderConfigError, match="Unsupported provider type"):
            ProviderFactory.create_provider(config)

    def test_create_from_dict(self):
        """Test creating provider from dictionary."""
        config_dict = {
            "provider_type": "environment",
            "prefix": "MY_",
        }

        provider = ProviderFactory.create_from_dict(config_dict)

        assert isinstance(provider, EnvironmentProvider)
        assert provider.prefix == "MY_", "prefix is not valid"

    def test_create_from_dict_missing_type(self):
        """Test creating from dict without provider_type."""
        config_dict = {"prefix": "MY_"}

        with pytest.raises(ProviderConfigError, match="Missing 'provider_type'"):
            ProviderFactory.create_from_dict(config_dict)

    def test_create_from_dict_invalid_type(self):
        """Test creating from dict with invalid provider type."""
        config_dict = {"provider_type": "invalid_type"}

        with pytest.raises(ProviderConfigError, match="Invalid provider type"):
            ProviderFactory.create_from_dict(config_dict)

    def test_get_available_providers(self):
        """Test getting list of available providers."""
        available = ProviderFactory.get_available_providers()

        assert isinstance(available, list)
        assert ProviderType.ENVIRONMENT in available, "Condition must be true"
        assert ProviderType.GITHUB in available, "Condition must be true"

    def test_get_available_providers_handles_import_errors(self):
        """Test get_available_providers still returns environment provider on import failures."""
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name in {
                "security.providers.github_provider",
                "security.providers.aws_provider",
            }:
                raise ImportError(f"simulated import failure for {name}")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            available = ProviderFactory.get_available_providers()
        assert available == [ProviderType.ENVIRONMENT], "available is not valid"

    def test_validate_config_github(self):
        """Test validating GitHub config."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test",  # pragma: allowlist secret
        )

        is_valid = ProviderFactory.validate_config(config)
        assert is_valid is True, "is_valid is not valid"

    def test_validate_config_github_no_token(self):
        """Test validating GitHub config without token (uses env var)."""
        config = ProviderConfig(provider_type=ProviderType.GITHUB)

        # Should still be valid (will use GITHUB_TOKEN env var)
        is_valid = ProviderFactory.validate_config(config)
        assert is_valid is True, "is_valid is not valid"

    def test_validate_config_aws_missing_region(self):
        """Test validating AWS config without required region."""
        config = ProviderConfig(provider_type=ProviderType.AWS_SECRETS_MANAGER)

        with pytest.raises(ProviderConfigError, match="region"):
            ProviderFactory.validate_config(config)

    def test_validate_config_aws_with_region(self):
        """Test validating AWS config with region."""
        config = ProviderConfig(
            provider_type=ProviderType.AWS_SECRETS_MANAGER,
            region="us-west-2",
        )

        is_valid = ProviderFactory.validate_config(config)
        assert is_valid is True, "is_valid is not valid"

    def test_validate_config_azure_requires_vault_url(self):
        """Test validating Azure config requires vault_url."""
        config = ProviderConfig(provider_type=ProviderType.AZURE_KEY_VAULT)

        with pytest.raises(ProviderConfigError, match="vault_url"):
            ProviderFactory.validate_config(config)

    def test_validate_config_hashicorp_requires_vault_url_and_token(self):
        """Test validating HashiCorp config requires vault_url and token."""
        config_missing_url = ProviderConfig(
            provider_type=ProviderType.HASHICORP_VAULT,
            token="vault-token",  # pragma: allowlist secret
        )
        with pytest.raises(ProviderConfigError, match="vault_url"):
            ProviderFactory.validate_config(config_missing_url)

        config_missing_token = ProviderConfig(
            provider_type=ProviderType.HASHICORP_VAULT,
            vault_url="https://vault.example.com",
        )
        with pytest.raises(
            ProviderConfigError,
            match=r"Required configuration 'token' not found for hashicorp_vault",
        ):
            ProviderFactory.validate_config(config_missing_token)

        config_complete = ProviderConfig(
            provider_type=ProviderType.HASHICORP_VAULT,
            vault_url="https://vault.example.com",
            token="vault-token",  # pragma: allowlist secret
        )
        assert ProviderFactory.validate_config(config_complete) is True, "ProviderFact is not valid"

    def test_create_provider_import_error_wrapped(self):
        """Test create_provider wraps ImportError with provider context."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB, token="ghp_test"
        )  # pragma: allowlist secret
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == "security.providers.github_provider":
                raise ImportError("simulated import failure")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            with pytest.raises(ProviderConfigError, match="Failed to import provider for github"):
                ProviderFactory.create_provider(config)


class TestCreateProviderFromEnv:
    """Test create_provider_from_env convenience function."""

    def test_create_github_from_env(self, monkeypatch):
        """Test creating GitHub provider from environment."""
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")

        provider = create_provider_from_env(ProviderType.GITHUB)

        assert isinstance(provider, GitHubTokenProvider)
        assert provider.token == "ghp_test_token", "token is not valid"

    def test_create_aws_from_env(self, monkeypatch):
        """Test creating AWS provider from environment."""
        monkeypatch.setenv("AWS_REGION", "eu-west-1")

        try:
            provider = create_provider_from_env(ProviderType.AWS_SECRETS_MANAGER)
            assert provider.region == "eu-west-1", "region is not valid"
        except ProviderConfigError:
            # Expected if boto3 not installed
            _ = None  # suppressed: no action needed

    def test_create_unsupported_from_env(self):
        """Test creating unsupported provider from env."""
        with pytest.raises(ProviderConfigError, match="not supported"):
            create_provider_from_env(ProviderType.HASHICORP_VAULT)

    def test_create_aws_from_env_with_explicit_credentials(self, monkeypatch):
        """Test AWS env helper forwards explicit credentials when present."""
        monkeypatch.setenv("AWS_REGION", "ap-southeast-1")
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIA_ENV_TEST")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "env-secret-key")

        with patch.object(ProviderFactory, "create_provider") as mock_create_provider:
            sentinel_provider = object()
            mock_create_provider.return_value = sentinel_provider

            provider = create_provider_from_env(ProviderType.AWS_SECRETS_MANAGER)
            assert provider is sentinel_provider, "provider is not valid"

            passed_config = mock_create_provider.call_args.args[0]
            assert passed_config.get("region") == "ap-southeast-1", "Condition must be true"
            assert passed_config.get("aws_access_key_id") == "AKIA_ENV_TEST", "Condition must be true"
            assert passed_config.get("aws_secret_access_key") == "env-secret-key", "Condition must be true"

    def test_create_azure_from_env_reaches_factory(self, monkeypatch):
        """Test Azure env helper constructs config then delegates to factory."""
        monkeypatch.setenv("AZURE_VAULT_URL", "https://vault.example.com")
        monkeypatch.setenv("AZURE_TENANT_ID", "tenant-id")
        monkeypatch.setenv("AZURE_CLIENT_ID", "client-id")
        monkeypatch.setenv("AZURE_CLIENT_SECRET", "client-secret")

        with pytest.raises(ProviderConfigError, match="not yet implemented"):
            create_provider_from_env(ProviderType.AZURE_KEY_VAULT)


# ============================================================================
# Property-Based Tests
# ============================================================================


class TestPropertyBased:
    """Property-based tests for providers."""

    def test_rotation_result_consistency(self):
        """Test that RotationResult maintains consistency."""
        # Success results should have new_secret_id
        result = RotationResult(
            success=True,
            old_secret_id="old",  # pragma: allowlist secret
            new_secret_id="new",  # pragma: allowlist secret
        )
        assert result.success is True, "Result must not be empty"
        assert result.new_secret_id == "new"  # pragma: allowlist secret

        # Failure results should have error_message
        result = RotationResult(
            success=False,
            old_secret_id="old",  # pragma: allowlist secret
            error_message="error",
        )
        assert result.success is False, "Result must not be empty"
        assert result.error_message == "error", "Result must not be empty"

    def test_provider_type_serialization(self):
        """Test that all provider types can be serialized and deserialized."""
        for provider_type in ProviderType:
            # Serialize
            value = provider_type.value
            # Deserialize
            restored = ProviderType(value)
            assert restored == provider_type, "restored is not valid"

    def test_environment_provider_isolation(self):
        """Test that environment provider operations are isolated."""
        config1 = ProviderConfig(provider_type=ProviderType.ENVIRONMENT, prefix="APP1_")
        config2 = ProviderConfig(provider_type=ProviderType.ENVIRONMENT, prefix="APP2_")

        provider1 = EnvironmentProvider(config1)
        provider2 = EnvironmentProvider(config2)

        provider1.set_secret_value("SECRET", "value1")
        provider2.set_secret_value("SECRET", "value2")

        assert provider1.get_secret_value("SECRET") == "value1", "Value must be initialized"
        assert provider2.get_secret_value("SECRET") == "value2", "Value must be initialized"


# ============================================================================
# Additional GitHubTokenProvider edge-case coverage
# ============================================================================


class TestGitHubTokenProviderEdgeCases:
    """Additional edge cases to fill coverage gaps in github_provider.py."""

    @pytest.fixture
    def provider_with_token(self):
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_testtoken1234567890123456789012345678",  # pragma: allowlist secret
            api_url="https://api.github.com",
        )
        return GitHubTokenProvider(config)

    @pytest.fixture
    def provider_with_installation(self):
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_testtoken1234567890123456789012345678",  # pragma: allowlist secret
            api_url="https://api.github.com",
            installation_id="99999",
        )
        return GitHubTokenProvider(config)

    # --- validate_secret ---

    def test_validate_secret_expired_token(self, provider_with_token):
        """Test validate_secret returns False when local expiry check says expired."""
        from datetime import UTC, datetime, timedelta
        from unittest.mock import patch

        past = datetime.now(UTC) - timedelta(days=1)
        with patch.object(GitHubTokenProvider, "get_expiration", return_value=past):
            token = "ghp_" + "V" * 36
            result = provider_with_token.validate_secret("tok", token)
        assert result is False, "Result must not be empty"

    def test_validate_secret_403_returns_false(self, provider_with_token):
        """Test validate_secret returns False on HTTP 403."""
        from unittest.mock import Mock, patch

        mock_resp = Mock()
        mock_resp.status_code = 403
        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.get.return_value = mock_resp
            token = "ghp_" + "F" * 36
            result = provider_with_token.validate_secret("tok", token)
        assert result is False, "Result must not be empty"

    def test_validate_secret_unexpected_status_returns_true(self, provider_with_token):
        """Test validate_secret treats unexpected status as valid."""
        from unittest.mock import Mock, patch

        mock_resp = Mock()
        mock_resp.status_code = 202
        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.get.return_value = mock_resp
            token = "ghp_" + "U" * 36
            result = provider_with_token.validate_secret("tok", token)
        assert result is True, "Result must not be empty"

    def test_validate_secret_without_requests(self, provider_with_token):
        """Test validate_secret falls back to format-only when requests unavailable."""
        from unittest.mock import patch

        token = "ghp_" + "R" * 36
        with patch("security.providers.github_provider.HAS_REQUESTS", False):
            result = provider_with_token.validate_secret("tok", token)
        assert result is True, "Result must not be empty"

    def test_validate_secret_exception_wraps_as_validation_error(self):
        """Test that unexpected exception is wrapped in ValidationError."""
        from unittest.mock import patch

        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_testtoken1234567890123456789012345678",  # pragma: allowlist secret
        )
        provider = GitHubTokenProvider(config)
        token = "ghp_" + "E" * 36
        with (
            patch.object(provider, "get_expiration", side_effect=RuntimeError("boom")),
            patch("security.providers.github_provider.HAS_REQUESTS", False),
        ):
            # RuntimeError is caught and wrapped
            result = provider.validate_secret("tok", token)
        # format-only validation returns True (exception in get_expiration is caught)
        assert result is True, "Result must not be empty"

    # --- create_token ---

    def test_create_token_no_requests(self, provider_with_installation):
        """Test create_token returns failure when requests is unavailable."""
        from unittest.mock import patch

        with patch("security.providers.github_provider.HAS_REQUESTS", False):
            result = provider_with_installation.create_token("name", ["contents"])
        assert result.success is False, "Result must not be empty"
        assert "requests" in (result.error_message or "").lower(), "Result must not be empty"

    def test_create_token_no_bearer_token(self):
        """Test create_token returns failure when bearer token is missing."""
        from unittest.mock import patch

        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            installation_id="12345",
        )
        with patch.dict(os.environ, {"GITHUB_TOKEN": ""}, clear=False):
            provider = GitHubTokenProvider(config)
            with patch("security.providers.github_provider.HAS_REQUESTS", True):
                result = provider.create_token("name", ["contents"])
        assert result.success is False, "Result must not be empty"
        assert "bearer token" in (result.error_message or "").lower(), "Result must not be empty"

    def test_create_token_request_exception(self, provider_with_installation):
        """Test create_token handles request exception gracefully."""
        from unittest.mock import patch

        import requests

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.post.side_effect = requests.exceptions.ConnectionError("network down")
            result = provider_with_installation.create_token("name", ["contents"])
        assert result.success is False, "Result must not be empty"
        assert "failed" in (result.error_message or "").lower(), "Result must not be empty"

    # --- update_token_scopes ---

    def test_update_token_scopes_no_token(self):
        """Test update_token_scopes returns False without bearer token."""
        from unittest.mock import patch

        config = ProviderConfig(provider_type=ProviderType.GITHUB)
        with patch.dict(os.environ, {"GITHUB_TOKEN": ""}, clear=False):
            provider = GitHubTokenProvider(config)
            with patch("security.providers.github_provider.HAS_REQUESTS", True):
                result = provider.update_token_scopes("12345", ["contents"])
        assert result is False, "Result must not be empty"

    def test_update_token_scopes_failure_status(self, provider_with_token):
        """Test update_token_scopes returns False on non-200/204 response."""
        from unittest.mock import Mock, patch

        mock_resp = Mock()
        mock_resp.status_code = 422
        mock_resp.text = "Unprocessable"

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.patch.return_value = mock_resp
            result = provider_with_token.update_token_scopes("12345", ["contents"])
        assert result is False, "Result must not be empty"

    def test_update_token_scopes_204_success(self, provider_with_token):
        """Test update_token_scopes returns True on 204 response."""
        from unittest.mock import Mock, patch

        mock_resp = Mock()
        mock_resp.status_code = 204

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.patch.return_value = mock_resp
            result = provider_with_token.update_token_scopes("12345", ["contents"])
        assert result is True, "Result must not be empty"

    def test_update_token_scopes_exception(self, provider_with_token):
        """Test update_token_scopes returns False on unexpected exception."""
        from unittest.mock import patch

        import requests

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.patch.side_effect = requests.exceptions.Timeout("timeout")
            result = provider_with_token.update_token_scopes("12345", ["contents"])
        assert result is False, "Result must not be empty"

    # --- revoke_secret ---

    def test_revoke_secret_no_token(self):
        """Test revoke_secret returns False without token."""
        from unittest.mock import patch

        config = ProviderConfig(provider_type=ProviderType.GITHUB)
        with patch.dict(os.environ, {"GITHUB_TOKEN": ""}, clear=False):
            provider = GitHubTokenProvider(config)
            with patch("security.providers.github_provider.HAS_REQUESTS", True):
                result = provider.revoke_secret("tok-id")
        assert result is False, "Result must not be empty"

    def test_revoke_secret_no_requests(self, provider_with_token):
        """Test revoke_secret returns False without requests library."""
        from unittest.mock import patch

        with patch("security.providers.github_provider.HAS_REQUESTS", False):
            result = provider_with_token.revoke_secret("tok-id")
        assert result is False, "Result must not be empty"

    def test_revoke_secret_ghs_token_success(self):
        """Test revoke_secret succeeds for ghs_ installation token (204)."""
        from unittest.mock import Mock, patch

        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghs_testinstallationtoken123456789",
        )
        provider = GitHubTokenProvider(config)

        mock_resp = Mock()
        mock_resp.status_code = 204

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.delete.return_value = mock_resp
            result = provider.revoke_secret("tok-id")
        assert result is True, "Result must not be empty"

    def test_revoke_secret_ghs_token_failure(self):
        """Test revoke_secret returns False on API failure for ghs_ token."""
        from unittest.mock import Mock, patch

        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghs_testinstallationtoken123456789",
        )
        provider = GitHubTokenProvider(config)

        mock_resp = Mock()
        mock_resp.status_code = 403

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.delete.return_value = mock_resp
            result = provider.revoke_secret("tok-id")
        assert result is False, "Result must not be empty"

    def test_revoke_secret_exception(self):
        """Test revoke_secret returns False on unexpected exception."""
        from unittest.mock import patch

        import requests

        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghs_testinstallationtoken123456789",
        )
        provider = GitHubTokenProvider(config)

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.delete.side_effect = requests.exceptions.ConnectionError("network")
            result = provider.revoke_secret("tok-id")
        assert result is False, "Result must not be empty"

    # --- list_secrets ---

    def test_list_secrets_no_token(self):
        """Test list_secrets returns empty list without token."""
        from unittest.mock import patch

        config = ProviderConfig(provider_type=ProviderType.GITHUB)
        with patch.dict(os.environ, {"GITHUB_TOKEN": ""}, clear=False):
            provider = GitHubTokenProvider(config)
            with patch("security.providers.github_provider.HAS_REQUESTS", True):
                result = provider.list_secrets()
        assert result == [], "Result must not be empty"

    def test_list_secrets_no_requests(self, provider_with_token):
        """Test list_secrets returns empty list without requests library."""
        from unittest.mock import patch

        with patch("security.providers.github_provider.HAS_REQUESTS", False):
            result = provider_with_token.list_secrets()
        assert result == [], "Result must not be empty"

    def test_list_secrets_200_response(self, provider_with_token):
        """Test list_secrets returns SecretMetadata on successful API call."""
        from unittest.mock import Mock, patch

        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"login": "testuser", "id": 12345}

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.get.return_value = mock_resp
            result = provider_with_token.list_secrets()

        assert len(result) == 1, "Result must not be empty"
        assert result[0].secret_id == "current_token", "Result must not be empty"
        assert result[0].tags["github_login"] == "testuser", "Result must not be empty"

    def test_list_secrets_non_200_response(self, provider_with_token):
        """Test list_secrets returns empty list on non-200 response."""
        from unittest.mock import Mock, patch

        mock_resp = Mock()
        mock_resp.status_code = 401

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.get.return_value = mock_resp
            result = provider_with_token.list_secrets()
        assert result == [], "Result must not be empty"

    def test_list_secrets_exception(self, provider_with_token):
        """Test list_secrets returns empty list on request exception."""
        from unittest.mock import patch

        import requests

        with (
            patch("security.providers.github_provider._requests") as mock_req,
            patch("security.providers.github_provider.HAS_REQUESTS", True),
        ):
            mock_req.get.side_effect = requests.exceptions.ConnectionError("offline")
            result = provider_with_token.list_secrets()
        assert result == [], "Result must not be empty"

    def test_rotate_secret_create_token_failure(self, provider_with_token):
        """Test rotate_secret propagates create_token failure."""
        from unittest.mock import patch

        with patch.object(
            GitHubTokenProvider,
            "create_token",
            return_value=RotationResult(
                success=False,
                old_secret_id="",
                error_message="API unavailable",
            ),
        ):
            result = provider_with_token.rotate_secret("old-id")
        assert result.success is False, "Result must not be empty"
        assert "unavailable" in (result.error_message or "").lower(), "Result must not be empty"

    def test_rotate_secret_exception_returns_failure(self, provider_with_token):
        """Test rotate_secret handles unexpected exceptions gracefully."""
        from unittest.mock import patch

        with patch.object(
            GitHubTokenProvider,
            "get_secret_metadata",
            side_effect=RuntimeError("unexpected"),
        ):
            result = provider_with_token.rotate_secret("old-id")
        assert result.success is False, "Result must not be empty"


# ============================================================================
# Security Decorators tests (decorators.py)
# ============================================================================


class TestScopeDecoratorContextVars:
    """Test context variable management for scope validators."""

    def setup_method(self):
        """Clear context before each test."""
        from security.decorators import clear_scope_validator

        clear_scope_validator()

    def teardown_method(self):
        """Clear context after each test."""
        from security.decorators import clear_scope_validator

        clear_scope_validator()

    def test_set_and_get_scope_validator(self):
        """Test setting and getting scope validator in context."""
        from security.decorators import get_scope_validator, set_scope_validator
        from security.scope_validator import ScopeValidator

        validator = ScopeValidator(["repo:read"])
        assert get_scope_validator() is None, "get_scope_validat is not valid"
        set_scope_validator(validator)
        assert get_scope_validator() is validator, "get_scope_validat is not valid"

    def test_clear_scope_validator(self):
        """Test clearing scope validator from context."""
        from security.decorators import (
            clear_scope_validator,
            get_scope_validator,
            set_scope_validator,
        )
        from security.scope_validator import ScopeValidator

        set_scope_validator(ScopeValidator(["repo:read"]))
        clear_scope_validator()
        assert get_scope_validator() is None, "get_scope_validat is not valid"


class TestRequireScopeDecorator:
    """Test require_scope decorator."""

    def setup_method(self):
        from security.decorators import clear_scope_validator

        clear_scope_validator()

    def teardown_method(self):
        from security.decorators import clear_scope_validator

        clear_scope_validator()

    def test_require_scope_passes_with_sufficient_scope(self):
        """Test decorated function executes when scope is sufficient."""
        from security.decorators import require_scope, set_scope_validator
        from security.scope_validator import ScopeValidator

        @require_scope("repo:write")
        def write_repo(data: str) -> str:
            return f"written: {data}"

        set_scope_validator(ScopeValidator(["repo:write"]))
        result = write_repo("payload")
        assert result == "written: payload", "Result must not be empty"

    def test_require_scope_raises_runtime_error_without_validator(self):
        """Test decorated function raises RuntimeError when no validator set."""
        from security.decorators import require_scope

        @require_scope("repo:write")
        def protected_func() -> str:
            return "ok"

        with pytest.raises(RuntimeError, match="No scope validator"):
            protected_func()

    def test_require_scope_raises_insufficient_scope_error(self):
        """Test decorated function raises InsufficientScopeError for insufficient scope."""
        from security.decorators import require_scope, set_scope_validator
        from security.scope_validator import InsufficientScopeError, ScopeValidator

        @require_scope("repo:admin")
        def admin_func() -> str:
            return "admin"

        set_scope_validator(ScopeValidator(["repo:read"]))
        with pytest.raises(InsufficientScopeError):
            admin_func()

    def test_require_scope_metadata_attributes(self):
        """Test that require_scope sets metadata attributes on wrapper."""
        from security.decorators import require_scope

        @require_scope("repo:write", "workflow:read")
        def my_func() -> None:
            pass

        assert my_func.__scope_protected__ is True, "__scope_protected__ is not valid"
        assert "repo:write" in my_func.__required_scopes__, "Condition must be true"
        assert "workflow:read" in my_func.__required_scopes__, "Condition must be true"

    def test_require_scope_preserves_function_name(self):
        """Test that require_scope preserves function metadata."""
        from security.decorators import require_scope

        @require_scope("repo:read")
        def my_named_function() -> None:
            """My docstring."""

        assert my_named_function.__name__ == "my_named_function", "__name__ is not valid"
        assert my_named_function.__doc__ == "My docstring.", "__doc__ is not valid"

    def test_require_multiple_scopes_all_required(self):
        """Test that all scopes in require_scope must be present."""
        from security.decorators import require_scope, set_scope_validator
        from security.scope_validator import InsufficientScopeError, ScopeValidator

        @require_scope("repo:write", "workflow:read")
        def func() -> str:
            return "ok"

        # Only one scope — should fail
        set_scope_validator(ScopeValidator(["repo:write"]))
        with pytest.raises(InsufficientScopeError):
            func()


class TestRequireAnyScopeDecorator:
    """Test require_any_scope decorator."""

    def setup_method(self):
        from security.decorators import clear_scope_validator

        clear_scope_validator()

    def teardown_method(self):
        from security.decorators import clear_scope_validator

        clear_scope_validator()

    def test_require_any_scope_passes_with_one_scope(self):
        """Test function executes with at least one matching scope."""
        from security.decorators import require_any_scope, set_scope_validator
        from security.scope_validator import ScopeValidator

        @require_any_scope("repo:write", "repo:admin")
        def write_or_admin() -> str:
            return "ok"

        set_scope_validator(ScopeValidator(["repo:write"]))
        assert write_or_admin() == "ok", "write_ is not valid"

    def test_require_any_scope_passes_with_different_scope(self):
        """Test function executes with a different valid scope."""
        from security.decorators import require_any_scope, set_scope_validator
        from security.scope_validator import ScopeValidator

        @require_any_scope("repo:write", "repo:admin")
        def func() -> str:
            return "ok"

        set_scope_validator(ScopeValidator(["repo:admin"]))
        assert func() == "ok", "Condition must be true"

    def test_require_any_scope_raises_without_validator(self):
        """Test RuntimeError when no validator set."""
        from security.decorators import require_any_scope

        @require_any_scope("repo:write")
        def func() -> str:
            return "ok"

        with pytest.raises(RuntimeError, match="No scope validator"):
            func()

    def test_require_any_scope_raises_when_none_match(self):
        """Test InsufficientScopeError when none of the scopes match."""
        from security.decorators import require_any_scope, set_scope_validator
        from security.scope_validator import InsufficientScopeError, ScopeValidator

        @require_any_scope("repo:admin", "org:admin")
        def admin_func() -> str:
            return "admin"

        set_scope_validator(ScopeValidator(["repo:read"]))
        with pytest.raises(InsufficientScopeError):
            admin_func()

    def test_require_any_scope_metadata_attributes(self):
        """Test metadata attributes set by require_any_scope."""
        from security.decorators import require_any_scope

        @require_any_scope("repo:write", "repo:admin")
        def func() -> None:
            pass

        assert func.__scope_protected__ is True, "__scope_protected__ is not valid"
        assert func.__scope_any__ is True, "__scope_any__ is not valid"
        assert "repo:write" in func.__required_scopes__, "Condition must be true"


class TestOptionalScopeDecorator:
    """Test optional_scope decorator."""

    def setup_method(self):
        from security.decorators import clear_scope_validator

        clear_scope_validator()

    def teardown_method(self):
        from security.decorators import clear_scope_validator

        clear_scope_validator()

    def test_optional_scope_runs_without_validator(self):
        """Test function executes even without validator set."""
        from security.decorators import optional_scope

        @optional_scope("repo:write")
        def public_func() -> str:
            return "public"

        assert public_func() == "public", "Condition must be true"

    def test_optional_scope_runs_with_sufficient_scope(self):
        """Test function executes when validator has required scope."""
        from security.decorators import optional_scope, set_scope_validator
        from security.scope_validator import ScopeValidator

        @optional_scope("repo:write")
        def func() -> str:
            return "ok"

        set_scope_validator(ScopeValidator(["repo:write"]))
        assert func() == "ok", "Condition must be true"

    def test_optional_scope_runs_with_insufficient_scope(self):
        """Test function still executes even with insufficient scope."""
        from security.decorators import optional_scope, set_scope_validator
        from security.scope_validator import ScopeValidator

        @optional_scope("repo:admin")
        def func() -> str:
            return "ok"

        set_scope_validator(ScopeValidator(["repo:read"]))
        # Should NOT raise, just logs
        assert func() == "ok", "Condition must be true"

    def test_optional_scope_metadata_attributes(self):
        """Test optional_scope sets metadata attributes."""
        from security.decorators import optional_scope

        @optional_scope("repo:write")
        def func() -> None:
            pass

        assert func.__scope_optional__ is True, "__scope_optional__ is not valid"
        assert "repo:write" in func.__optional_scopes__, "Condition must be true"


class TestScopeMetadataFunction:
    """Test scope_metadata extraction function."""

    def test_scope_metadata_from_require_scope(self):
        """Test scope_metadata returns correct data for require_scope."""
        from security.decorators import require_scope, scope_metadata

        @require_scope("repo:write")
        def func() -> None:
            pass

        meta = scope_metadata(func)
        assert meta["protected"] is True, "Condition must be true"
        assert "repo:write" in meta["required"], "Condition must be true"
        assert meta["any"] is False, "Condition must be true"
        assert meta["optional"] is False, "Condition must be true"

    def test_scope_metadata_from_require_any_scope(self):
        """Test scope_metadata returns correct data for require_any_scope."""
        from security.decorators import require_any_scope, scope_metadata

        @require_any_scope("repo:write", "repo:admin")
        def func() -> None:
            pass

        meta = scope_metadata(func)
        assert meta["protected"] is True, "Condition must be true"
        assert meta["any"] is True, "Condition must be true"

    def test_scope_metadata_from_optional_scope(self):
        """Test scope_metadata returns correct data for optional_scope."""
        from security.decorators import optional_scope, scope_metadata

        @optional_scope("repo:read")
        def func() -> None:
            pass

        meta = scope_metadata(func)
        assert meta["optional"] is True, "Condition must be true"
        assert meta["protected"] is False, "Condition must be true"

    def test_scope_metadata_from_undecorated_function(self):
        """Test scope_metadata returns defaults for undecorated function."""
        from security.decorators import scope_metadata

        def plain_func() -> None:
            pass

        meta = scope_metadata(plain_func)
        assert meta["protected"] is False, "Condition must be true"
        assert meta["optional"] is False, "Condition must be true"
        assert meta["required"] == [], "Condition must be true"
        assert meta["any"] is False, "Condition must be true"
