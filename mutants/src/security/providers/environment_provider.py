"""Environment-based provider for testing and development.

This module provides a simple provider that reads secrets from environment
variables, useful for testing and local development.

Part of PS-05 Enhancement: Multi-Provider Support - Priority 4
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any, Optional

from security.providers.base import (
    ProviderConfig,
    ProviderType,
    RotationResult,
    SecretMetadata,
    SecretProvider,
    SecretType,
)

logger = logging.getLogger(__name__)


class EnvironmentProvider(SecretProvider):
    """Provider that reads secrets from environment variables.

    Useful for:
    - Local development
    - Testing
    - Simple deployments without secret management service

    Example:
        >>> os.environ["MY_SECRET"] = "secret_value"
        >>> config = ProviderConfig(provider_type=ProviderType.ENVIRONMENT)
        >>> provider = EnvironmentProvider(config)
        >>> provider.validate_secret("MY_SECRET")
        True
    """

    def __init__(self, config: ProviderConfig):
        """Initialize environment provider.

        Args:
            config: Provider configuration
        """
        self.config = config
        self.prefix = config.get("prefix", "")
        logger.info("Environment provider initialized")

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.ENVIRONMENT

    def rotate_secret(self, secret_id: str, **kwargs: Any) -> RotationResult:
        """Rotate environment variable secret.

        For environment provider, rotation is not automatic.
        Returns instructions for manual rotation.

        Args:
            secret_id: Environment variable name
            **kwargs: Not used

        Returns:
            RotationResult with instructions
        """
        full_name = f"{self.prefix}{secret_id}"

        if full_name not in os.environ:
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"Environment variable {full_name} not found",
            )

        return RotationResult(
            success=False,
            old_secret_id=secret_id,
            error_message=(
                "Environment provider does not support automatic rotation. "
                f"Manually update environment variable: {full_name}"
            ),
        )

    def validate_secret(self, secret_id: str, secret_value: Optional[str] = None) -> bool:
        """Validate environment variable exists.

        Args:
            secret_id: Environment variable name
            secret_value: Optional value to compare against

        Returns:
            True if variable exists (and matches value if provided)
        """
        full_name = f"{self.prefix}{secret_id}"
        env_value = os.getenv(full_name)

        if env_value is None:
            return False

        if secret_value is not None:
            return env_value == secret_value

        return True

    def get_secret_metadata(self, secret_id: str) -> SecretMetadata:
        """Get metadata for environment variable.

        Args:
            secret_id: Environment variable name

        Returns:
            SecretMetadata with basic info
        """
        full_name = f"{self.prefix}{secret_id}"

        return SecretMetadata(
            secret_id=secret_id,
            secret_type=SecretType.GENERIC,
            provider=ProviderType.ENVIRONMENT,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            expires_at=None,  # No expiration
            rotation_policy=None,
            tags={"source": "environment", "name": full_name},
            scopes=None,
        )

    def get_expiration(self, secret_id: str) -> Optional[datetime]:
        """Get expiration (always None for environment variables).

        Args:
            secret_id: Environment variable name

        Returns:
            None (no expiration)
        """
        return None

    def get_secret_value(self, secret_id: str) -> Optional[str]:
        """Get secret value from environment.

        Args:
            secret_id: Environment variable name

        Returns:
            Secret value or None if not found
        """
        full_name = f"{self.prefix}{secret_id}"
        return os.getenv(full_name)

    def set_secret_value(self, secret_id: str, value: str) -> bool:
        """Set secret value in environment (for testing).

        Args:
            secret_id: Environment variable name
            value: New value

        Returns:
            True if set successfully
        """
        full_name = f"{self.prefix}{secret_id}"
        os.environ[full_name] = value
        logger.info("Set environment variable via EnvironmentSecretProvider")
        return True

    def list_secrets(self, filter_tags: Optional[dict[str, str]] = None) -> list[SecretMetadata]:
        """List all environment variables with prefix.

        Args:
            filter_tags: Not used

        Returns:
            List of SecretMetadata for matching variables
        """
        secrets = []

        for name in os.environ:
            if name.startswith(self.prefix):
                # Remove prefix to get secret_id
                secret_id = name[len(self.prefix) :]
                try:
                    metadata = self.get_secret_metadata(secret_id)
                    secrets.append(metadata)
                except (ValueError, TypeError, RuntimeError) as e:
                    # Don't log environment variable names for security
                    logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")

        return secrets
