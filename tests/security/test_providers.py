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

from __future__ import annotations

# botocore is needed by two AWS provider tests (ClientError); skip gracefully when absent
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
        assert ProviderType.GITHUB.value == "github"
        assert ProviderType.AWS_SECRETS_MANAGER.value == "aws_secrets_manager"
        assert ProviderType.AZURE_KEY_VAULT.value == "azure_key_vault"
        assert ProviderType.HASHICORP_VAULT.value == "hashicorp_vault"
        assert ProviderType.ENVIRONMENT.value == "environment"

    def test_enum_membership(self):
        """Test enum membership checks."""
        assert ProviderType.GITHUB in ProviderType
        # Enum values can be checked with 'in' operator
        assert "github" in ProviderType._value2member_map_

    def test_enum_from_value(self):
        """Test creating enum from string value."""
        assert ProviderType("github") == ProviderType.GITHUB
        with pytest.raises(ValueError):
            ProviderType("invalid_provider")


class TestSecretType:
    """Test SecretType enum."""

    def test_all_secret_types(self):
        """Test all secret type enum values."""
        assert SecretType.TOKEN.value == "token"
        assert SecretType.API_KEY.value == "api_key"
        assert SecretType.PASSWORD.value == "password"
        assert SecretType.CERTIFICATE.value == "certificate"
        assert SecretType.SSH_KEY.value == "ssh_key"
        assert SecretType.GENERIC.value == "generic"


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
        assert metadata.secret_id == "test-id"
        assert metadata.secret_type == SecretType.TOKEN
        assert metadata.provider == ProviderType.GITHUB
        assert metadata.expires_at is None
        assert metadata.rotation_policy is None
        assert metadata.tags is None
        assert metadata.scopes is None

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

        assert metadata.expires_at == expires
        assert metadata.rotation_policy == "auto_rotate"
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
            new_secret_value="new-value",
        )
        assert result.success is True
        assert result.old_secret_id == "old-id"
        assert result.new_secret_id == "new-id"
        assert result.new_secret_value == "new-value"
        assert result.error_message is None

    def test_failure_result(self):
        """Test failed rotation result."""
        result = RotationResult(
            success=False,
            old_secret_id="old-id",
            error_message="Rotation failed: API error",
        )
        assert result.success is False
        assert result.error_message == "Rotation failed: API error"
        assert result.new_secret_id is None
        assert result.new_secret_value is None


class TestExceptions:
    """Test custom exception classes."""

    def test_secret_provider_error(self):
        """Test base SecretProviderError."""
        with pytest.raises(SecretProviderError, match="Base error"):
            raise SecretProviderError("Base error")

    def test_provider_config_error(self):
        """Test ProviderConfigError."""
        with pytest.raises(ProviderConfigError, match="Config invalid"):
            raise ProviderConfigError("Config invalid")

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
            token="ghp_test",
            api_url="https://api.github.com",
        )
        assert config.provider_type == ProviderType.GITHUB
        assert config.get("token") == "ghp_test"
        assert config.get("api_url") == "https://api.github.com"

    def test_get_with_default(self):
        """Test get with default value."""
        config = ProviderConfig(provider_type=ProviderType.GITHUB)
        assert config.get("missing_key", "default") == "default"
        assert config.get("missing_key") is None

    def test_require_existing(self):
        """Test require with existing key."""
        config = ProviderConfig(
            provider_type=ProviderType.AWS_SECRETS_MANAGER,
            region="us-east-1",
        )
        assert config.require("region") == "us-east-1"

    def test_require_missing(self):
        """Test require with missing key raises error."""
        config = ProviderConfig(provider_type=ProviderType.AWS_SECRETS_MANAGER)
        with pytest.raises(ProviderConfigError, match="Required configuration 'region' not found"):
            config.require("region")

    def test_repr(self):
        """Test string representation."""
        config = ProviderConfig(provider_type=ProviderType.GITHUB)
        assert "ProviderConfig" in repr(config)
        assert "github" in repr(config)


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
        assert provider.get_scopes("test") == []

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
        assert provider.provider_name == "AWS Secrets Manager"

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
        assert "ConcreteProvider" in repr(provider)
        assert "github" in repr(provider)


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
            token="ghp_test_token_1234567890",
            api_url="https://api.github.com",
        )

    def test_initialization_with_token(self, github_config):
        """Test initialization with explicit token."""
        provider = GitHubTokenProvider(github_config)
        assert provider.provider_type == ProviderType.GITHUB
        assert provider.token == "ghp_test_token_1234567890"
        assert provider.api_url == "https://api.github.com"

    def test_initialization_without_token(self):
        """Test initialization without token (uses env var)."""
        config = ProviderConfig(provider_type=ProviderType.GITHUB)
        provider = GitHubTokenProvider(config)
        assert provider.token is None or provider.token == os.getenv("GITHUB_TOKEN")

    def test_rotate_secret_success(self, github_config):
        """Test successful token rotation."""
        provider = GitHubTokenProvider(github_config)

        # Mock create_token to control the return value
        with patch.object(GitHubTokenProvider, 'create_token') as mock_create:
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

            assert result.success is True
            assert result.old_secret_id == "old-token-id"
            assert result.new_secret_id is not None
            assert result.new_secret_value is not None
            assert "ghp_" in result.new_secret_value
            mock_create.assert_called_once()

    def test_rotate_secret_with_revoke(self, github_config):
        """Test token rotation with old token revocation."""
        provider = GitHubTokenProvider(github_config)

        # Mock create_token to control the return value
        with patch.object(GitHubTokenProvider, 'create_token') as mock_create:
            mock_create.return_value = RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id="new-token-id",
                new_secret_value="ghp_new_token_value",  # pragma: allowlist secret
            )

            with patch.object(GitHubTokenProvider, 'revoke_secret') as mock_revoke:
                mock_revoke.return_value = True

                result = provider.rotate_secret(
                    "old-token-id",
                    revoke_old=True,
                )

                assert result.success is True
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
        assert is_valid is True

    def test_validate_secret_invalid_format(self, github_config):
        """Test validation rejects tokens with invalid format."""
        provider = GitHubTokenProvider(github_config)
        # Too short — won't match the regex, so validate_secret returns False
        # before making any API call
        is_valid = provider.validate_secret("token-id", "ghp_tooshort")
        assert is_valid is False

    def test_validate_secret_api_401(self, github_config):
        """Test validation returns False when GitHub API returns 401."""
        provider = GitHubTokenProvider(github_config)
        token = "ghp_" + "B" * 36
        mock_response = Mock()
        mock_response.status_code = 401
        with patch("requests.get", return_value=mock_response):
            is_valid = provider.validate_secret("token-id", token)
        assert is_valid is False

    def test_validate_secret_network_error_degrades_gracefully(self, github_config):
        """Test that network errors fall back to format-only validation."""
        import requests as real_requests
        provider = GitHubTokenProvider(github_config)
        token = "ghp_" + "C" * 36
        with patch("requests.get", side_effect=real_requests.exceptions.ConnectionError("offline")):
            is_valid = provider.validate_secret("token-id", token)
        # Format is valid so should return True after graceful degradation
        assert is_valid is True

    def test_validate_secret_no_token(self, github_config):
        """Test validation fails when no token provided."""
        # Ensure no token in config or environment
        config = ProviderConfig(provider_type=ProviderType.GITHUB)
        with patch.dict(os.environ, {}, clear=False):
            # Remove GITHUB_TOKEN from environment for this test
            os.environ.pop('GITHUB_TOKEN', None)
            provider = GitHubTokenProvider(config)

            with pytest.raises(ValidationError, match="No token provided"):
                provider.validate_secret("token-id", None)

    def test_get_secret_metadata(self, github_config):
        """Test getting token metadata."""
        provider = GitHubTokenProvider(github_config)
        metadata = provider.get_secret_metadata("token-id")

        assert metadata.secret_id == "token-id"
        assert metadata.secret_type == SecretType.TOKEN
        assert metadata.provider == ProviderType.GITHUB
        assert metadata.expires_at is not None
        assert metadata.scopes == ["repo", "workflow"]

    def test_get_expiration(self, github_config):
        """Test getting token expiration."""
        provider = GitHubTokenProvider(github_config)
        expiration = provider.get_expiration("token-id")

        assert expiration is not None
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
        assert result.success is False
        assert "installation_id" in (result.error_message or "")

    def test_create_token_with_installation_id(self, github_config):
        """Test create_token calls GitHub API when installation_id is set."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test_token_1234567890",
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

        with patch("security.providers.github_provider._requests") as mock_req, \
             patch("security.providers.github_provider.HAS_REQUESTS", True):
            mock_req.post.return_value = mock_resp
            result = provider.create_token(
                name="test-token",
                scopes=["contents", "workflows"],
            )

        assert result.success is True
        assert result.new_secret_value == "ghs_test_installation_token_value"  # pragma: allowlist secret  # noqa: E501
        assert result.new_secret_id == "99"

    def test_create_token_invalid_pat_scopes(self, github_config):
        """Test create_token rejects PAT-style scopes."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test_token_1234567890",
            api_url="https://api.github.com",
            installation_id="12345",
        )
        provider = GitHubTokenProvider(config)

        result = provider.create_token(
            name="test-token",
            scopes=["repo", "workflow"],  # PAT-style — should be rejected
        )

        assert result.success is False
        assert "Invalid installation permission" in (result.error_message or "")

    def test_create_token_empty_token_response(self, github_config):
        """Test create_token fails closed when API returns 201 but no token."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test_token_1234567890",
            api_url="https://api.github.com",
            installation_id="12345",
        )
        provider = GitHubTokenProvider(config)

        mock_resp = Mock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"id": 99, "expires_at": "2026-03-18T00:00:00Z"}

        with patch("security.providers.github_provider._requests") as mock_req, \
             patch("security.providers.github_provider.HAS_REQUESTS", True):
            mock_req.post.return_value = mock_resp
            result = provider.create_token(name="t", scopes=["contents"])

        assert result.success is False
        assert "no token" in (result.error_message or "").lower()

    def test_create_token_api_failure(self, github_config):
        """Test create_token handles API errors gracefully."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test_token_1234567890",
            api_url="https://api.github.com",
            installation_id="12345",
        )
        provider = GitHubTokenProvider(config)

        mock_resp = Mock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"

        with patch("security.providers.github_provider._requests") as mock_req, \
             patch("security.providers.github_provider.HAS_REQUESTS", True):
            mock_req.post.return_value = mock_resp
            result = provider.create_token(name="t", scopes=["contents"])

        assert result.success is False
        assert "403" in (result.error_message or "")

    def test_update_token_scopes(self, github_config):
        """Test updating token scopes calls GitHub API."""
        provider = GitHubTokenProvider(github_config)

        mock_resp = Mock()
        mock_resp.status_code = 200

        with patch("security.providers.github_provider._requests") as mock_req, \
             patch("security.providers.github_provider.HAS_REQUESTS", True):
            mock_req.patch.return_value = mock_resp
            success = provider.update_token_scopes(
                "12345",
                ["contents", "workflows", "issues"],
            )

        assert success is True

    def test_update_token_scopes_no_requests(self, github_config):
        """Test update_token_scopes returns False without requests library."""
        provider = GitHubTokenProvider(github_config)

        with patch("security.providers.github_provider.HAS_REQUESTS", False):
            success = provider.update_token_scopes("12345", ["contents"])

        assert success is False

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
        assert success is False

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
            aws_secret_access_key="secret_test_key",
        )

    def test_initialization_requires_boto3(self, aws_config):
        """Test that AWS provider requires boto3."""
        # This will either succeed if boto3 is installed or fail appropriately
        try:
            from security.providers.aws_provider import AWSSecretsManagerProvider
            provider = AWSSecretsManagerProvider(aws_config)
            assert provider.provider_type == ProviderType.AWS_SECRETS_MANAGER
            assert provider.region == "us-east-1"
        except ProviderConfigError as e:
            assert "boto3 required" in str(e)

    @patch("security.providers.aws_provider.HAS_BOTO3", False)
    def test_initialization_without_boto3_raises_error(self, aws_config):
        """Test initialization fails without boto3."""
        from security.providers.aws_provider import AWSSecretsManagerProvider

        with pytest.raises(ProviderConfigError, match="boto3 required"):
            AWSSecretsManagerProvider(aws_config)

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

        assert result.success is True
        assert result.metadata["version_id"] == "new-version-id"

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

        assert result.success is False
        assert "ResourceNotFoundException" in result.error_message

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
        assert is_valid is True

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
        assert is_valid is False

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

        assert metadata.secret_id == "test-secret"
        assert metadata.secret_type == SecretType.GENERIC
        assert metadata.provider == ProviderType.AWS_SECRETS_MANAGER
        assert metadata.tags == {"env": "test"}

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_get_expiration_always_none(self, mock_boto3, aws_config):
        """Test that AWS secrets don't have expiration."""
        mock_boto3.client.return_value = Mock()

        from security.providers.aws_provider import AWSSecretsManagerProvider
        provider = AWSSecretsManagerProvider(aws_config)

        expiration = provider.get_expiration("test-secret")
        assert expiration is None

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_get_secret_value_string(self, mock_boto3, aws_config):
        """Test getting secret string value."""
        mock_client = Mock()
        mock_client.get_secret_value.return_value = {
            "SecretString": "my-secret-value"
        }
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider
        provider = AWSSecretsManagerProvider(aws_config)

        value = provider.get_secret_value("test-secret")
        assert value == "my-secret-value"

    @patch("security.providers.aws_provider.HAS_BOTO3", True)
    @patch("security.providers.aws_provider.boto3")
    def test_get_secret_value_binary(self, mock_boto3, aws_config):
        """Test getting secret binary value."""
        mock_client = Mock()
        mock_client.get_secret_value.return_value = {
            "SecretBinary": b"binary-secret"
        }
        mock_boto3.client.return_value = mock_client

        from security.providers.aws_provider import AWSSecretsManagerProvider
        provider = AWSSecretsManagerProvider(aws_config)

        value = provider.get_secret_value("test-secret")
        assert isinstance(value, str)  # Base64 encoded

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
            secret_value="secret-value",
            description="Test secret",
            tags={"env": "test"},
        )

        assert result.success is True
        assert result.new_secret_id == "test-secret"

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
        assert success is True

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
        assert len(secrets) == 2


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
        assert provider.provider_type == ProviderType.ENVIRONMENT
        assert provider.prefix == "TEST_"

    def test_initialization_no_prefix(self):
        """Test initialization without prefix."""
        config = ProviderConfig(provider_type=ProviderType.ENVIRONMENT)
        provider = EnvironmentProvider(config)
        assert provider.prefix == ""

    def test_rotate_secret_returns_manual_instruction(self, env_config):
        """Test that rotation returns manual instruction."""
        os.environ["TEST_SECRET"] = "value"
        provider = EnvironmentProvider(env_config)

        result = provider.rotate_secret("SECRET")

        assert result.success is False
        assert "manual" in result.error_message.lower()
        assert "TEST_SECRET" in result.error_message

    def test_rotate_secret_not_found(self, env_config):
        """Test rotation when env var doesn't exist."""
        provider = EnvironmentProvider(env_config)

        result = provider.rotate_secret("MISSING")

        assert result.success is False
        assert "not found" in result.error_message

    def test_validate_secret_exists(self, env_config):
        """Test validation when env var exists."""
        os.environ["TEST_SECRET"] = "value"
        provider = EnvironmentProvider(env_config)

        is_valid = provider.validate_secret("SECRET")
        assert is_valid is True

    def test_validate_secret_not_exists(self, env_config):
        """Test validation when env var doesn't exist."""
        provider = EnvironmentProvider(env_config)

        is_valid = provider.validate_secret("MISSING")
        assert is_valid is False

    def test_validate_secret_with_value_match(self, env_config):
        """Test validation with matching value."""
        os.environ["TEST_SECRET"] = "expected_value"
        provider = EnvironmentProvider(env_config)

        is_valid = provider.validate_secret("SECRET", "expected_value")
        assert is_valid is True

    def test_validate_secret_with_value_mismatch(self, env_config):
        """Test validation with non-matching value."""
        os.environ["TEST_SECRET"] = "actual_value"
        provider = EnvironmentProvider(env_config)

        is_valid = provider.validate_secret("SECRET", "wrong_value")
        assert is_valid is False

    def test_get_secret_metadata(self, env_config):
        """Test getting metadata."""
        provider = EnvironmentProvider(env_config)
        metadata = provider.get_secret_metadata("SECRET")

        assert metadata.secret_id == "SECRET"
        assert metadata.secret_type == SecretType.GENERIC
        assert metadata.provider == ProviderType.ENVIRONMENT
        assert metadata.expires_at is None
        assert metadata.tags["name"] == "TEST_SECRET"

    def test_get_expiration_always_none(self, env_config):
        """Test that expiration is always None."""
        provider = EnvironmentProvider(env_config)
        expiration = provider.get_expiration("SECRET")
        assert expiration is None

    def test_get_secret_value(self, env_config):
        """Test getting secret value."""
        os.environ["TEST_SECRET"] = "my_value"
        provider = EnvironmentProvider(env_config)

        value = provider.get_secret_value("SECRET")
        assert value == "my_value"

    def test_get_secret_value_not_found(self, env_config):
        """Test getting non-existent secret."""
        provider = EnvironmentProvider(env_config)

        value = provider.get_secret_value("MISSING")
        assert value is None

    def test_set_secret_value(self, env_config):
        """Test setting secret value."""
        provider = EnvironmentProvider(env_config)

        success = provider.set_secret_value("NEW_SECRET", "new_value")
        assert success is True
        assert os.environ["TEST_NEW_SECRET"] == "new_value"

    def test_list_secrets_with_prefix(self, env_config):
        """Test listing secrets with prefix filter."""
        os.environ["TEST_SECRET1"] = "value1"
        os.environ["TEST_SECRET2"] = "value2"
        os.environ["OTHER_SECRET"] = "value3"

        provider = EnvironmentProvider(env_config)
        secrets = provider.list_secrets()

        assert len(secrets) == 2
        secret_ids = [s.secret_id for s in secrets]
        assert "SECRET1" in secret_ids
        assert "SECRET2" in secret_ids


# ============================================================================
# Test Provider Factory (provider_factory.py)
# ============================================================================


class TestProviderFactory:
    """Test ProviderFactory class."""

    def test_create_github_provider(self):
        """Test creating GitHub provider."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test",
        )

        provider = ProviderFactory.create_provider(config)

        assert isinstance(provider, GitHubTokenProvider)
        assert provider.provider_type == ProviderType.GITHUB

    def test_create_environment_provider(self):
        """Test creating environment provider."""
        config = ProviderConfig(provider_type=ProviderType.ENVIRONMENT)

        provider = ProviderFactory.create_provider(config)

        assert isinstance(provider, EnvironmentProvider)
        assert provider.provider_type == ProviderType.ENVIRONMENT

    def test_create_aws_provider(self):
        """Test creating AWS provider (if boto3 available)."""
        config = ProviderConfig(
            provider_type=ProviderType.AWS_SECRETS_MANAGER,
            region="us-east-1",
        )

        try:
            provider = ProviderFactory.create_provider(config)
            assert provider.provider_type == ProviderType.AWS_SECRETS_MANAGER
        except ProviderConfigError as e:
            # Expected if boto3 not installed
            assert "boto3" in str(e).lower()

    def test_create_unsupported_provider(self):
        """Test creating unsupported provider raises error."""
        config = ProviderConfig(provider_type=ProviderType.AZURE_KEY_VAULT)

        with pytest.raises(ProviderConfigError, match="not yet implemented"):
            ProviderFactory.create_provider(config)

    def test_create_from_dict(self):
        """Test creating provider from dictionary."""
        config_dict = {
            "provider_type": "environment",
            "prefix": "MY_",
        }

        provider = ProviderFactory.create_from_dict(config_dict)

        assert isinstance(provider, EnvironmentProvider)
        assert provider.prefix == "MY_"

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
        assert ProviderType.ENVIRONMENT in available
        assert ProviderType.GITHUB in available

    def test_validate_config_github(self):
        """Test validating GitHub config."""
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token="ghp_test",
        )

        is_valid = ProviderFactory.validate_config(config)
        assert is_valid is True

    def test_validate_config_github_no_token(self):
        """Test validating GitHub config without token (uses env var)."""
        config = ProviderConfig(provider_type=ProviderType.GITHUB)

        # Should still be valid (will use GITHUB_TOKEN env var)
        is_valid = ProviderFactory.validate_config(config)
        assert is_valid is True

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
        assert is_valid is True


class TestCreateProviderFromEnv:
    """Test create_provider_from_env convenience function."""

    def test_create_github_from_env(self, monkeypatch):
        """Test creating GitHub provider from environment."""
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")

        provider = create_provider_from_env(ProviderType.GITHUB)

        assert isinstance(provider, GitHubTokenProvider)
        assert provider.token == "ghp_test_token"

    def test_create_aws_from_env(self, monkeypatch):
        """Test creating AWS provider from environment."""
        monkeypatch.setenv("AWS_REGION", "eu-west-1")

        try:
            provider = create_provider_from_env(ProviderType.AWS_SECRETS_MANAGER)
            assert provider.region == "eu-west-1"
        except ProviderConfigError:
            # Expected if boto3 not installed
            pass

    def test_create_unsupported_from_env(self):
        """Test creating unsupported provider from env."""
        with pytest.raises(ProviderConfigError, match="not supported"):
            create_provider_from_env(ProviderType.HASHICORP_VAULT)


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
            old_secret_id="old",
            new_secret_id="new",
        )
        assert result.success is True
        assert result.new_secret_id == "new"

        # Failure results should have error_message
        result = RotationResult(
            success=False,
            old_secret_id="old",
            error_message="error",
        )
        assert result.success is False
        assert result.error_message == "error"

    def test_provider_type_serialization(self):
        """Test that all provider types can be serialized and deserialized."""
        for provider_type in ProviderType:
            # Serialize
            value = provider_type.value
            # Deserialize
            restored = ProviderType(value)
            assert restored == provider_type

    def test_environment_provider_isolation(self):
        """Test that environment provider operations are isolated."""
        config1 = ProviderConfig(provider_type=ProviderType.ENVIRONMENT, prefix="APP1_")
        config2 = ProviderConfig(provider_type=ProviderType.ENVIRONMENT, prefix="APP2_")

        provider1 = EnvironmentProvider(config1)
        provider2 = EnvironmentProvider(config2)

        provider1.set_secret_value("SECRET", "value1")
        provider2.set_secret_value("SECRET", "value2")

        assert provider1.get_secret_value("SECRET") == "value1"
        assert provider2.get_secret_value("SECRET") == "value2"
