"""Security providers for secret management.

This package provides implementations of various secret providers:
- AWS Secrets Manager
- GitHub Tokens
- Environment Variables
- Base provider interfaces

Usage:
    from security.providers import AWSSecretsManagerProvider, GitHubTokenProvider
"""

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

# AWS provider is optional (requires boto3)
try:
    from security.providers.aws_provider import AWSSecretsManagerProvider

    __all__ = [
        # Base
        "ProviderType",
        "SecretType",
        "SecretMetadata",
        "RotationResult",
        "SecretProviderError",
        "ProviderConfigError",
        "RotationError",
        "ValidationError",
        "SecretProvider",
        "TokenProvider",
        "ProviderConfig",
        # Implementations
        "EnvironmentProvider",
        "GitHubTokenProvider",
        "AWSSecretsManagerProvider",
    ]
except ImportError:
    # boto3 not available - AWS provider not exposed
    __all__ = [
        # Base
        "ProviderType",
        "SecretType",
        "SecretMetadata",
        "RotationResult",
        "SecretProviderError",
        "ProviderConfigError",
        "RotationError",
        "ValidationError",
        "SecretProvider",
        "TokenProvider",
        "ProviderConfig",
        # Implementations
        "EnvironmentProvider",
        "GitHubTokenProvider",
    ]
