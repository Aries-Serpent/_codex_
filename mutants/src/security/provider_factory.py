"""Provider factory for multi-cloud secret management.

This module provides a factory pattern for creating secret provider instances
based on configuration, supporting dynamic provider selection.

Part of PS-05 Enhancement: Multi-Provider Support - Priority 4
"""

from __future__ import annotations

import logging
from typing import Any

from security.providers.base import (
    ProviderConfig,
    ProviderConfigError,
    ProviderType,
    SecretProvider,
)

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory for creating secret provider instances.

    Supports dynamic provider loading based on configuration,
    with fallback handling and validation.

    Example:
        >>> config = ProviderConfig(
        ...     provider_type=ProviderType.GITHUB,
        ...     token=os.getenv("GITHUB_TOKEN")
        ... )
        >>> provider = ProviderFactory.create_provider(config)
        >>> isinstance(provider, GitHubTokenProvider)
        True
    """

    @staticmethod
    def create_provider(config: ProviderConfig) -> SecretProvider:
        """Create provider instance from configuration.

        Args:
            config: Provider configuration

        Returns:
            SecretProvider instance

        Raises:
            ProviderConfigError: If provider type unsupported or config invalid
        """
        provider_type = config.provider_type

        try:
            if provider_type == ProviderType.GITHUB:
                from security.providers.github_provider import GitHubTokenProvider

                return GitHubTokenProvider(config)

            if provider_type == ProviderType.AWS_SECRETS_MANAGER:
                from security.providers.aws_provider import AWSSecretsManagerProvider

                return AWSSecretsManagerProvider(config)

            if provider_type == ProviderType.AZURE_KEY_VAULT:
                # Future implementation
                raise ProviderConfigError("Azure Key Vault provider not yet implemented")

            if provider_type == ProviderType.HASHICORP_VAULT:
                # Future implementation
                raise ProviderConfigError("HashiCorp Vault provider not yet implemented")

            if provider_type == ProviderType.ENVIRONMENT:
                # For testing - returns stub provider
                from security.providers.environment_provider import EnvironmentProvider

                return EnvironmentProvider(config)

            raise ProviderConfigError(f"Unsupported provider type: {provider_type}")

        except ImportError as e:
            raise ProviderConfigError(
                f"Failed to import provider for {provider_type.value}: {e}"
            ) from e

    @staticmethod
    def create_from_dict(config_dict: dict[str, Any]) -> SecretProvider:
        """Create provider from dictionary configuration.

        Args:
            config_dict: Configuration dictionary with 'provider_type' key

        Returns:
            SecretProvider instance

        Raises:
            ProviderConfigError: If configuration invalid
        """
        if "provider_type" not in config_dict:
            raise ProviderConfigError("Missing 'provider_type' in configuration")

        # Parse provider type
        provider_type_str = config_dict.pop("provider_type")
        try:
            provider_type = ProviderType(provider_type_str)
        except ValueError as err:
            msg = f"Invalid provider type: {provider_type_str}"
            raise ProviderConfigError(msg) from err

        # Create config and provider
        config = ProviderConfig(provider_type=provider_type, **config_dict)
        return ProviderFactory.create_provider(config)

    @staticmethod
    def get_available_providers() -> list[ProviderType]:
        """Get list of available provider types.

        Checks which providers can be imported and returns
        only those that are available.

        Returns:
            List of available ProviderType values
        """
        available = []

        # Check GitHub
        try:
            from security.providers.github_provider import (
                GitHubTokenProvider as GitHubTokenProvider,
            )

            available.append(ProviderType.GITHUB)
        except ImportError:
            # GitHub provider dependencies not available (e.g., requests library)
            # This is expected in minimal installations; gracefully skip
            logger.debug("Suppressed exception in handler", exc_info=True)
        # Check AWS
        try:
            from security.providers.aws_provider import (
                AWSSecretsManagerProvider as AWSSecretsManagerProvider,
            )

            available.append(ProviderType.AWS_SECRETS_MANAGER)
        except ImportError:
            # AWS provider dependencies not available (e.g., boto3 library)
            # This is expected when AWS features are not needed; gracefully skip
            logger.debug("Suppressed exception in handler", exc_info=True)
        # Environment always available
        available.append(ProviderType.ENVIRONMENT)

        return available

    @staticmethod
    def validate_config(config: ProviderConfig) -> bool:
        """Validate provider configuration.

        Checks that required configuration keys are present
        for the specified provider type.

        Args:
            config: Provider configuration

        Returns:
            True if configuration is valid

        Raises:
            ProviderConfigError: If configuration invalid
        """
        provider_type = config.provider_type

        # Provider-specific validation
        if provider_type == ProviderType.GITHUB:
            # Require token or allow environment variable
            if not config.get("token"):
                logger.warning("GitHub token not in config - will use GITHUB_TOKEN env var")

        elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
            # Require region
            config.require("region")

        elif provider_type == ProviderType.AZURE_KEY_VAULT:
            # Require vault_url
            config.require("vault_url")

        elif provider_type == ProviderType.HASHICORP_VAULT:
            # Require vault_url and token
            config.require("vault_url")
            config.require("token")

        return True


# Convenience function for quick provider creation
def create_provider_from_env(provider_type: ProviderType) -> SecretProvider:
    """Create provider using environment variables for configuration.

    Args:
        provider_type: Type of provider to create

    Returns:
        SecretProvider instance

    Raises:
        ProviderConfigError: If environment variables not set

    Example:
        >>> # With GITHUB_TOKEN environment variable set
        >>> provider = create_provider_from_env(ProviderType.GITHUB)
    """
    import os

    if provider_type == ProviderType.GITHUB:
        config = ProviderConfig(provider_type=ProviderType.GITHUB, token=os.getenv("GITHUB_TOKEN"))

    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }

        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            config_dict["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")

        config = ProviderConfig(**config_dict)

    elif provider_type == ProviderType.AZURE_KEY_VAULT:
        config = ProviderConfig(
            provider_type=ProviderType.AZURE_KEY_VAULT,
            vault_url=os.getenv("AZURE_VAULT_URL"),
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )

    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )

    return ProviderFactory.create_provider(config)
