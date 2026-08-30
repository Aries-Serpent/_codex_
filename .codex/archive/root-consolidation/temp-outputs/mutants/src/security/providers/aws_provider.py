"""AWS Secrets Manager Provider implementation.

This module implements the SecretProvider interface for AWS Secrets Manager,
supporting secret rotation, retrieval, and management.

Part of PS-05 Enhancement: Multi-Provider Support - Priority 4
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, Optional

from security.providers.base import (
    ProviderConfig,
    ProviderConfigError,
    ProviderType,
    RotationResult,
    SecretMetadata,
    SecretProvider,
    SecretType,
    ValidationError,
)

logger = logging.getLogger(__name__)

# Optional boto3 import - must be at module level for mocking in tests
try:
    import boto3
    from botocore.exceptions import ClientError

    HAS_BOTO3 = True
except ImportError:
    # Create placeholder module for boto3 to allow test patching
    # This enables @patch("security.providers.aws_provider.boto3") to work
    import sys
    from types import ModuleType

    boto3 = ModuleType("boto3")
    # Add common attributes to prevent AttributeErrors in tests
    boto3.client = lambda *args, **kwargs: None  # type: ignore
    boto3.session = None  # type: ignore
    sys.modules.setdefault("boto3", boto3)
    ClientError = Exception
    HAS_BOTO3 = False
    logger.warning("boto3 not installed - AWS provider will be stub only")


class AWSSecretsManagerProvider(SecretProvider):
    """AWS Secrets Manager provider.

    Supports:
    - Secret creation and rotation
    - Automatic rotation with Lambda
    - Version management
    - Tag-based organization

    Example:
        >>> config = ProviderConfig(
        ...     provider_type=ProviderType.AWS_SECRETS_MANAGER,
        ...     region="us-east-1",
        ...     aws_access_key_id="...",
        ...     aws_secret_access_key="..."
        ... )
        >>> provider = AWSSecretsManagerProvider(config)
        >>> result = provider.rotate_secret("my-secret")
    """

    def __init__(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.

        Args:
            config: Provider configuration with AWS credentials

        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )

        self.config = config
        self.region = config.require("region")

        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")

        self.client = boto3.client("secretsmanager", region_name=self.region, **session_kwargs)

        logger.info(f"AWS secure-store provider initialized (region={self.region})")

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.AWS_SECRETS_MANAGER

    def rotate_secret(self, secret_id: str, **kwargs: Any) -> RotationResult:
        """Rotate AWS secret.

        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules

        Returns:
            RotationResult with rotation details

        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )

            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                },
            )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")

            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}",
            )
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.error("AWS rotation failed: <ERROR_TYPE>")
            return RotationResult(success=False, old_secret_id=secret_id, error_message=str(e))

    def validate_secret(self, secret_id: str, secret_value: Optional[str] = None) -> bool:
        """Validate AWS secret exists and is accessible.

        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)

        Returns:
            True if secret is valid

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e

    def get_secret_metadata(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.

        Args:
            secret_id: Secret name or ARN

        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)

            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)

            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)

            # Parse tags
            tags = {tag["Key"]: tag["Value"] for tag in response.get("Tags", [])}

            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )

        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e

    def get_expiration(self, secret_id: str) -> Optional[datetime]:
        """Get secret expiration.

        AWS Secrets Manager doesn't have expiration concept.

        Args:
            secret_id: Secret name or ARN

        Returns:
            None (no expiration)
        """
        return None

    def get_secret_value(self, secret_id: str) -> str:
        """Get secret value from AWS.

        Args:
            secret_id: Secret name or ARN

        Returns:
            Secret value string

        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)

            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            import base64

            return base64.b64encode(response["SecretBinary"]).decode("utf-8")

        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e

    def create_secret(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> RotationResult:
        """Create new AWS secret.

        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags

        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }

            if description:
                create_kwargs["Description"] = description

            if tags:
                create_kwargs["Tags"] = [{"Key": k, "Value": v} for k, v in tags.items()]  # type: ignore[assignment]

            response = self.client.create_secret(**create_kwargs)

            return RotationResult(
                success=True,
                old_secret_id="",  # nosec B106
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                },
            )

        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",  # nosec B106
                error_message=str(e),
            )

    def delete_secret(self, secret_id: str, recovery_window_days: int = 30) -> bool:
        """Delete AWS secret (with recovery window).

        Args:
            secret_id: Secret name or ARN
            recovery_window_days: Days before permanent deletion

        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_secret(SecretId=secret_id, RecoveryWindowInDays=recovery_window_days)
            return True

        except ClientError as e:
            logger.error("Failed to delete secure-store entry: %s", type(e).__name__)
            return False

    def list_secrets(self, filter_tags: Optional[dict[str, str]] = None) -> list[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.

        Args:
            filter_tags: Optional tag filters

        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")

            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({"Key": "tag-key", "Values": [key]})
                    filters.append({"Key": "tag-value", "Values": [value]})

            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except (ValueError, TypeError, RuntimeError) as e:
                        logger.warning(
                            "Failed to get secure-store metadata: %s",
                            type(e).__name__,
                        )

            return secrets

        except ClientError as e:
            logger.error("Failed to list secure-store entries: %s", type(e).__name__)
            return []
