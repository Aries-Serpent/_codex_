"""Abstract base classes for secret providers.

This module defines the provider interface for multi-cloud secret management,
supporting GitHub, AWS Secrets Manager, Azure Key Vault, and HashiCorp Vault.

Part of PS-05 Enhancement: Multi-Provider Support - Priority 4
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported secret provider types."""

    GITHUB = "github"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"  # pragma: allowlist secret
    AZURE_KEY_VAULT = "azure_key_vault"
    HASHICORP_VAULT = "hashicorp_vault"
    ENVIRONMENT = "environment"  # For testing/development


class SecretType(Enum):
    """Types of secrets managed by providers."""

    TOKEN = "token"  # nosec B105  # pragma: allowlist secret
    API_KEY = "api_key"  # pragma: allowlist secret
    PASSWORD = "password"  # nosec B105  # pragma: allowlist secret
    CERTIFICATE = "certificate"
    SSH_KEY = "ssh_key"
    GENERIC = "generic"


@dataclass
class SecretMetadata:
    """Metadata about a secret."""

    secret_id: str
    secret_type: SecretType
    provider: ProviderType
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    rotation_policy: Optional[str] = None
    tags: Optional[dict[str, str]] = None
    scopes: Optional[list[str]] = None


@dataclass
class RotationResult:
    """Result of a secret rotation operation."""

    success: bool
    old_secret_id: str
    new_secret_id: Optional[str] = None
    new_secret_value: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class SecretProviderError(Exception):
    """Base exception for secret provider errors."""


class ProviderConfigError(SecretProviderError):
    """Raised when provider configuration is invalid."""


class RotationError(SecretProviderError):
    """Raised when secret rotation fails."""


class ValidationError(SecretProviderError):
    """Raised when secret validation fails."""


class SecretProvider(ABC):
    """Abstract base class for secret providers.

    All secret management providers must implement this interface
    to support token rotation, validation, and metadata retrieval.

    Example:
        >>> class MyProvider(SecretProvider):
        ...     def rotate_secret(self, secret_id: str) -> RotationResult:
        ...         # Implementation
        ...         pass
    """

    @abstractmethod
    def rotate_secret(self, secret_id: str, **kwargs: Any) -> RotationResult:
        """Rotate a secret to a new value.

        Args:
            secret_id: Identifier of secret to rotate
            **kwargs: Provider-specific options

        Returns:
            RotationResult with new secret details

        Raises:
            RotationError: If rotation fails
        """

    @abstractmethod
    def validate_secret(self, secret_id: str, secret_value: Optional[str] = None) -> bool:
        """Validate a secret is valid and not expired.

        Args:
            secret_id: Identifier of secret to validate
            secret_value: Optional secret value to validate

        Returns:
            True if secret is valid

        Raises:
            ValidationError: If validation fails
        """

    @abstractmethod
    def get_secret_metadata(self, secret_id: str) -> SecretMetadata:
        """Get metadata about a secret.

        Args:
            secret_id: Identifier of secret

        Returns:
            SecretMetadata with secret details

        Raises:
            SecretProviderError: If secret not found
        """

    @abstractmethod
    def get_expiration(self, secret_id: str) -> Optional[datetime]:
        """Get expiration date of a secret.

        Args:
            secret_id: Identifier of secret

        Returns:
            Expiration datetime or None if no expiration

        Raises:
            SecretProviderError: If secret not found
        """

    def get_scopes(self, secret_id: str) -> list[str]:
        """Get scopes/permissions associated with a secret.

        Default implementation returns empty list.
        Override in providers that support scopes (e.g., GitHub).

        Args:
            secret_id: Identifier of secret

        Returns:
            List of scope strings
        """
        return []

    def revoke_secret(self, secret_id: str) -> bool:
        """Revoke a secret immediately.

        Default implementation raises NotImplementedError.
        Override in providers that support revocation.

        Args:
            secret_id: Identifier of secret to revoke

        Returns:
            True if revoked successfully

        Raises:
            NotImplementedError: If provider doesn't support revocation
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support revocation")

    def list_secrets(self, filter_tags: Optional[dict[str, str]] = None) -> list[SecretMetadata]:
        """List all secrets managed by this provider.

        Default implementation raises NotImplementedError.
        Override in providers that support listing.

        Args:
            filter_tags: Optional tags to filter by

        Returns:
            List of SecretMetadata

        Raises:
            NotImplementedError: If provider doesn't support listing
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support listing")

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Get the provider type.

        Returns:
            ProviderType enum value
        """

    @property
    def provider_name(self) -> str:
        """Get human-readable provider name with proper acronym capitalization.

        Returns:
            Provider name string with correct casing for brands/acronyms
        """
        raw_value = self.provider_type.value
        # Explicit mappings preserve correct capitalization for acronyms/brands.
        provider_name_overrides = {
            "aws_secrets_manager": "AWS Secrets Manager",  # pragma: allowlist secret
            "github": "GitHub",
            "azure_key_vault": "Azure Key Vault",
            "hashicorp_vault": "HashiCorp Vault",
            "environment": "Environment",
        }
        return provider_name_overrides.get(
            raw_value,
            raw_value.replace("_", " ").title(),
        )

    def __repr__(self) -> str:
        """String representation of provider."""
        return f"<{self.__class__.__name__} provider={self.provider_type.value}>"


class TokenProvider(SecretProvider):
    """Specialized provider for API tokens/personal access tokens.

    Extends SecretProvider with token-specific functionality.
    """

    @abstractmethod
    def create_token(
        self, name: str, scopes: list[str], expires_in_days: Optional[int] = None
    ) -> RotationResult:
        """Create a new token.

        Args:
            name: Human-readable token name
            scopes: List of scopes/permissions
            expires_in_days: Optional expiration (days from now)

        Returns:
            RotationResult with new token details

        Raises:
            SecretProviderError: If creation fails
        """

    @abstractmethod
    def update_token_scopes(self, secret_id: str, scopes: list[str]) -> bool:
        """Update scopes for an existing token.

        Args:
            secret_id: Identifier of token
            scopes: New list of scopes

        Returns:
            True if updated successfully

        Raises:
            SecretProviderError: If update fails
        """


class ProviderConfig:
    """Configuration for secret providers.

    Example:
        >>> config = ProviderConfig(
        ...     provider_type=ProviderType.AWS_SECRETS_MANAGER,
        ...     region="us-east-1",
        ...     credentials={
        ...         "aws_access_key_id": "...",
        ...         "aws_secret_access_key": "..."
        ...     }
        ... )
    """

    def __init__(self, provider_type: ProviderType, **config: Any):
        """Initialize provider configuration.

        Args:
            provider_type: Type of provider
            **config: Provider-specific configuration
        """
        self.provider_type = provider_type
        self.config = config

    def get(self, key: str, default: Any | None = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def require(self, key: str) -> Any:
        """Get required configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value

        Raises:
            ProviderConfigError: If key not found
        """
        if key not in self.config:
            raise ProviderConfigError(
                f"Required configuration '{key}' not found for {self.provider_type.value}"
            )
        return self.config[key]

    def __repr__(self) -> str:
        """String representation."""
        return f"<ProviderConfig provider={self.provider_type.value}>"
