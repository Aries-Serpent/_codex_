"""Provider factory for multi-cloud secret management.

This module provides a factory pattern for creating secret provider instances
based on configuration, supporting dynamic provider selection.

Part of PS-05 Enhancement: Multi-Provider Support - Priority 4
"""

from __future__ import annotations

import logging
from typing import Dict, Any

from security.providers.base import (
    SecretProvider,
    ProviderType,
    ProviderConfig,
    ProviderConfigError,
)

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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
            
            elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
                from security.providers.aws_provider import AWSSecretsManagerProvider
                return AWSSecretsManagerProvider(config)
            
            elif provider_type == ProviderType.AZURE_KEY_VAULT:
                # Future implementation
                raise ProviderConfigError(
                    "Azure Key Vault provider not yet implemented"
                )
            
            elif provider_type == ProviderType.HASHICORP_VAULT:
                # Future implementation
                raise ProviderConfigError(
                    "HashiCorp Vault provider not yet implemented"
                )
            
            elif provider_type == ProviderType.ENVIRONMENT:
                # For testing - returns stub provider
                from security.providers.environment_provider import EnvironmentProvider
                return EnvironmentProvider(config)
            
            else:
                raise ProviderConfigError(
                    f"Unsupported provider type: {provider_type}"
                )
                
        except ImportError as e:
            raise ProviderConfigError(
                f"Failed to import provider for {provider_type.value}: {e}"
            ) from e
    
    @staticmethod
    def create_from_dict(config_dict: Dict[str, Any]) -> SecretProvider:
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
        except ValueError:
            raise ProviderConfigError(
                f"Invalid provider type: {provider_type_str}"
            )
        
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
            from security.providers.github_provider import GitHubTokenProvider  # noqa: F401 - Testing optional dependency availability
            available.append(ProviderType.GITHUB)
        except ImportError:
            # GitHub provider dependencies not available (e.g., requests library)
            # This is expected in minimal installations; gracefully skip
            pass
        
        # Check AWS
        try:
            from security.providers.aws_provider import AWSSecretsManagerProvider  # noqa: F401 - Testing optional dependency availability
            available.append(ProviderType.AWS_SECRETS_MANAGER)
        except ImportError:
            # AWS provider dependencies not available (e.g., boto3 library)
            # This is expected when AWS features are not needed; gracefully skip
            pass
        
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
def x_create_provider_from_env__mutmut_orig(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_1(provider_type: ProviderType) -> SecretProvider:
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
    
    if provider_type != ProviderType.GITHUB:
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_2(provider_type: ProviderType) -> SecretProvider:
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
        config = None
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_3(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=None,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_4(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=None
        )
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_5(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            token=os.getenv("GITHUB_TOKEN")
        )
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_6(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            )
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_7(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv(None)
        )
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_8(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("XXGITHUB_TOKENXX")
        )
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_9(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("github_token")
        )
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_10(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type != ProviderType.AWS_SECRETS_MANAGER:
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_11(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = None
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_12(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv(None, "us-east-1")
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_13(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", None)
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_14(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("us-east-1")
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_15(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", )
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_16(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("XXAWS_REGIONXX", "us-east-1")
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_17(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("aws_region", "us-east-1")
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_18(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "XXus-east-1XX")
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_19(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "US-EAST-1")
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_20(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = None
        
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_21(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "XXprovider_typeXX": ProviderType.AWS_SECRETS_MANAGER,
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_22(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "PROVIDER_TYPE": ProviderType.AWS_SECRETS_MANAGER,
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_23(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "XXregionXX": region,
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_24(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "REGION": region,
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_25(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv(None):
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_26(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("XXAWS_ACCESS_KEY_IDXX"):
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_27(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("aws_access_key_id"):
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_28(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["aws_access_key_id"] = None
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_29(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["XXaws_access_key_idXX"] = os.getenv("AWS_ACCESS_KEY_ID")
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_30(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_31(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["aws_access_key_id"] = os.getenv(None)
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_32(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["aws_access_key_id"] = os.getenv("XXAWS_ACCESS_KEY_IDXX")
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_33(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["aws_access_key_id"] = os.getenv("aws_access_key_id")
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_34(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            config_dict["aws_secret_access_key"] = None
        
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_35(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            config_dict["XXaws_secret_access_keyXX"] = os.getenv("AWS_SECRET_ACCESS_KEY")
        
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_36(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            config_dict["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
        
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_37(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            config_dict["aws_secret_access_key"] = os.getenv(None)
        
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_38(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            config_dict["aws_secret_access_key"] = os.getenv("XXAWS_SECRET_ACCESS_KEYXX")
        
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_39(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
    elif provider_type == ProviderType.AWS_SECRETS_MANAGER:
        region = os.getenv("AWS_REGION", "us-east-1")
        config_dict = {
            "provider_type": ProviderType.AWS_SECRETS_MANAGER,
            "region": region,
        }
        
        # Add credentials if provided (otherwise use IAM role)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config_dict["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            config_dict["aws_secret_access_key"] = os.getenv("aws_secret_access_key")
        
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_40(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
        
        config = None
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_41(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
    
    elif provider_type != ProviderType.AZURE_KEY_VAULT:
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_42(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
        config = None
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_43(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            provider_type=None,
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_44(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            vault_url=None,
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_45(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            tenant_id=None,
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_46(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            client_id=None,
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_47(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            client_secret=None,
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_48(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_49(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_50(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_51(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_52(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_53(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            vault_url=os.getenv(None),
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_54(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            vault_url=os.getenv("XXAZURE_VAULT_URLXX"),
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_55(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            vault_url=os.getenv("azure_vault_url"),
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_56(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            tenant_id=os.getenv(None),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_57(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            tenant_id=os.getenv("XXAZURE_TENANT_IDXX"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_58(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            tenant_id=os.getenv("azure_tenant_id"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_59(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            client_id=os.getenv(None),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_60(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            client_id=os.getenv("XXAZURE_CLIENT_IDXX"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_61(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            client_id=os.getenv("azure_client_id"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_62(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            client_secret=os.getenv(None),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_63(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            client_secret=os.getenv("XXAZURE_CLIENT_SECRETXX"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_64(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            client_secret=os.getenv("azure_client_secret"),
        )
    
    else:
        raise ProviderConfigError(
            f"Environment-based creation not supported for {provider_type.value}"
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_65(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
            None
        )
    
    return ProviderFactory.create_provider(config)


# Convenience function for quick provider creation
def x_create_provider_from_env__mutmut_66(provider_type: ProviderType) -> SecretProvider:
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
        config = ProviderConfig(
            provider_type=ProviderType.GITHUB,
            token=os.getenv("GITHUB_TOKEN")
        )
    
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
    
    return ProviderFactory.create_provider(None)

x_create_provider_from_env__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_provider_from_env__mutmut_1': x_create_provider_from_env__mutmut_1, 
    'x_create_provider_from_env__mutmut_2': x_create_provider_from_env__mutmut_2, 
    'x_create_provider_from_env__mutmut_3': x_create_provider_from_env__mutmut_3, 
    'x_create_provider_from_env__mutmut_4': x_create_provider_from_env__mutmut_4, 
    'x_create_provider_from_env__mutmut_5': x_create_provider_from_env__mutmut_5, 
    'x_create_provider_from_env__mutmut_6': x_create_provider_from_env__mutmut_6, 
    'x_create_provider_from_env__mutmut_7': x_create_provider_from_env__mutmut_7, 
    'x_create_provider_from_env__mutmut_8': x_create_provider_from_env__mutmut_8, 
    'x_create_provider_from_env__mutmut_9': x_create_provider_from_env__mutmut_9, 
    'x_create_provider_from_env__mutmut_10': x_create_provider_from_env__mutmut_10, 
    'x_create_provider_from_env__mutmut_11': x_create_provider_from_env__mutmut_11, 
    'x_create_provider_from_env__mutmut_12': x_create_provider_from_env__mutmut_12, 
    'x_create_provider_from_env__mutmut_13': x_create_provider_from_env__mutmut_13, 
    'x_create_provider_from_env__mutmut_14': x_create_provider_from_env__mutmut_14, 
    'x_create_provider_from_env__mutmut_15': x_create_provider_from_env__mutmut_15, 
    'x_create_provider_from_env__mutmut_16': x_create_provider_from_env__mutmut_16, 
    'x_create_provider_from_env__mutmut_17': x_create_provider_from_env__mutmut_17, 
    'x_create_provider_from_env__mutmut_18': x_create_provider_from_env__mutmut_18, 
    'x_create_provider_from_env__mutmut_19': x_create_provider_from_env__mutmut_19, 
    'x_create_provider_from_env__mutmut_20': x_create_provider_from_env__mutmut_20, 
    'x_create_provider_from_env__mutmut_21': x_create_provider_from_env__mutmut_21, 
    'x_create_provider_from_env__mutmut_22': x_create_provider_from_env__mutmut_22, 
    'x_create_provider_from_env__mutmut_23': x_create_provider_from_env__mutmut_23, 
    'x_create_provider_from_env__mutmut_24': x_create_provider_from_env__mutmut_24, 
    'x_create_provider_from_env__mutmut_25': x_create_provider_from_env__mutmut_25, 
    'x_create_provider_from_env__mutmut_26': x_create_provider_from_env__mutmut_26, 
    'x_create_provider_from_env__mutmut_27': x_create_provider_from_env__mutmut_27, 
    'x_create_provider_from_env__mutmut_28': x_create_provider_from_env__mutmut_28, 
    'x_create_provider_from_env__mutmut_29': x_create_provider_from_env__mutmut_29, 
    'x_create_provider_from_env__mutmut_30': x_create_provider_from_env__mutmut_30, 
    'x_create_provider_from_env__mutmut_31': x_create_provider_from_env__mutmut_31, 
    'x_create_provider_from_env__mutmut_32': x_create_provider_from_env__mutmut_32, 
    'x_create_provider_from_env__mutmut_33': x_create_provider_from_env__mutmut_33, 
    'x_create_provider_from_env__mutmut_34': x_create_provider_from_env__mutmut_34, 
    'x_create_provider_from_env__mutmut_35': x_create_provider_from_env__mutmut_35, 
    'x_create_provider_from_env__mutmut_36': x_create_provider_from_env__mutmut_36, 
    'x_create_provider_from_env__mutmut_37': x_create_provider_from_env__mutmut_37, 
    'x_create_provider_from_env__mutmut_38': x_create_provider_from_env__mutmut_38, 
    'x_create_provider_from_env__mutmut_39': x_create_provider_from_env__mutmut_39, 
    'x_create_provider_from_env__mutmut_40': x_create_provider_from_env__mutmut_40, 
    'x_create_provider_from_env__mutmut_41': x_create_provider_from_env__mutmut_41, 
    'x_create_provider_from_env__mutmut_42': x_create_provider_from_env__mutmut_42, 
    'x_create_provider_from_env__mutmut_43': x_create_provider_from_env__mutmut_43, 
    'x_create_provider_from_env__mutmut_44': x_create_provider_from_env__mutmut_44, 
    'x_create_provider_from_env__mutmut_45': x_create_provider_from_env__mutmut_45, 
    'x_create_provider_from_env__mutmut_46': x_create_provider_from_env__mutmut_46, 
    'x_create_provider_from_env__mutmut_47': x_create_provider_from_env__mutmut_47, 
    'x_create_provider_from_env__mutmut_48': x_create_provider_from_env__mutmut_48, 
    'x_create_provider_from_env__mutmut_49': x_create_provider_from_env__mutmut_49, 
    'x_create_provider_from_env__mutmut_50': x_create_provider_from_env__mutmut_50, 
    'x_create_provider_from_env__mutmut_51': x_create_provider_from_env__mutmut_51, 
    'x_create_provider_from_env__mutmut_52': x_create_provider_from_env__mutmut_52, 
    'x_create_provider_from_env__mutmut_53': x_create_provider_from_env__mutmut_53, 
    'x_create_provider_from_env__mutmut_54': x_create_provider_from_env__mutmut_54, 
    'x_create_provider_from_env__mutmut_55': x_create_provider_from_env__mutmut_55, 
    'x_create_provider_from_env__mutmut_56': x_create_provider_from_env__mutmut_56, 
    'x_create_provider_from_env__mutmut_57': x_create_provider_from_env__mutmut_57, 
    'x_create_provider_from_env__mutmut_58': x_create_provider_from_env__mutmut_58, 
    'x_create_provider_from_env__mutmut_59': x_create_provider_from_env__mutmut_59, 
    'x_create_provider_from_env__mutmut_60': x_create_provider_from_env__mutmut_60, 
    'x_create_provider_from_env__mutmut_61': x_create_provider_from_env__mutmut_61, 
    'x_create_provider_from_env__mutmut_62': x_create_provider_from_env__mutmut_62, 
    'x_create_provider_from_env__mutmut_63': x_create_provider_from_env__mutmut_63, 
    'x_create_provider_from_env__mutmut_64': x_create_provider_from_env__mutmut_64, 
    'x_create_provider_from_env__mutmut_65': x_create_provider_from_env__mutmut_65, 
    'x_create_provider_from_env__mutmut_66': x_create_provider_from_env__mutmut_66
}

def create_provider_from_env(*args, **kwargs):
    result = _mutmut_trampoline(x_create_provider_from_env__mutmut_orig, x_create_provider_from_env__mutmut_mutants, args, kwargs)
    return result 

create_provider_from_env.__signature__ = _mutmut_signature(x_create_provider_from_env__mutmut_orig)
x_create_provider_from_env__mutmut_orig.__name__ = 'x_create_provider_from_env'
