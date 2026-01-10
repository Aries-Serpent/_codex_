"""GitHub Token Provider implementation.

This module implements the SecretProvider interface for GitHub Personal
Access Tokens (PATs) and GitHub Apps, supporting token rotation, validation,
and scope management.

Part of PS-05 Enhancement: Multi-Provider Support - Priority 4
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, UTC
from typing import Optional, List, Dict, Any

from security.providers.base import (
    TokenProvider,
    ProviderType,
    SecretType,
    SecretMetadata,
    RotationResult,
    RotationError,
    ValidationError,
    ProviderConfig,
)

logger = logging.getLogger(__name__)


def _redact_identifier(identifier: str) -> str:
    """Redact sensitive identifier for logging.
    
    Args:
        identifier: Token ID, name, or other identifier
        
    Returns:
        Redacted version showing only first 4 characters
    """
    if not identifier or len(identifier) <= 4:
        return "***"
    return f"{identifier[:4]}***"


class GitHubTokenProvider(TokenProvider):
    """GitHub token provider for PATs and GitHub Apps.
    
    Supports:
    - Personal Access Token (PAT) validation
    - Fine-grained PAT creation/rotation
    - Scope/permission management
    - Token expiration tracking
    
    Example:
        >>> config = ProviderConfig(
        ...     provider_type=ProviderType.GITHUB,
        ...     api_url="https://api.github.com",
        ...     token=os.getenv("GITHUB_TOKEN")
        ... )
        >>> provider = GitHubTokenProvider(config)
        >>> result = provider.rotate_secret("my-token-id")
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize GitHub provider.
        
        Args:
            config: Provider configuration with GitHub API settings
        """
        self.config = config
        self.api_url = config.get("api_url", "https://api.github.com")
        self.token = config.get("token", os.getenv("GITHUB_TOKEN"))
        
        if not self.token:
            logger.warning("GitHub token not configured")
    
    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.GITHUB
    
    def rotate_secret(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate GitHub token.
        
        For fine-grained PATs, creates a new token with same scopes.
        For classic PATs, returns error (manual rotation required).
        
        Args:
            secret_id: Token ID or note
            **kwargs: Optional rotation parameters:
                - scopes: List of new scopes
                - expires_in_days: Days until expiration
                - note: Token description
                
        Returns:
            RotationResult with new token details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Get current token metadata
            metadata = self.get_secret_metadata(secret_id)
            
            # Extract rotation parameters
            scopes = kwargs.get("scopes", metadata.scopes or [])
            expires_in_days = kwargs.get("expires_in_days", 90)
            note = kwargs.get("note", f"Rotated token for {secret_id}")
            
            # Create new token
            new_token_result = self.create_token(
                name=note,
                scopes=scopes,
                expires_in_days=expires_in_days
            )
            
            if not new_token_result.success:
                return RotationResult(
                    success=False,
                    old_secret_id=secret_id,
                    error_message=new_token_result.error_message
                )
            
            # Revoke old token (optional, based on policy)
            if kwargs.get("revoke_old", False):
                try:
                    self.revoke_secret(secret_id)
                except Exception as e:
                    logger.warning(f"Failed to revoke old token: {e}")
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=new_token_result.new_secret_id,
                new_secret_value=new_token_result.new_secret_value,
                metadata={
                    "scopes": scopes,
                    "expires_in_days": expires_in_days,
                }
            )
            
        except Exception as e:
            logger.error(f"GitHub token rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def validate_secret(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate GitHub token.
        
        Args:
            secret_id: Token ID
            secret_value: Optional token value to validate
            
        Returns:
            True if token is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Use provided token or configured token
            token = secret_value or self.token
            
            if not token:
                raise ValidationError("No token provided for validation")
            
            # Make API request to validate token
            # This is a stub - actual implementation would use GitHub API
            # Example: GET /user with token authentication
            logger.info(f"Validating GitHub token: {_redact_identifier(secret_id)}")
            
            # Check expiration
            try:
                expiration = self.get_expiration(secret_id)
                if expiration and datetime.now(UTC) >= expiration:
                    logger.warning(f"Token {_redact_identifier(secret_id)} has expired")
                    return False
            except Exception as e:
                logger.debug(f"Could not check expiration: {e}")
            
            # TODO: Actual API validation
            # For now, return True if token exists
            return bool(token)
            
        except Exception as e:
            raise ValidationError(f"Token validation failed: {e}") from e
    
    def get_secret_metadata(self, secret_id: str) -> SecretMetadata:
        """Get GitHub token metadata.
        
        Args:
            secret_id: Token ID
            
        Returns:
            SecretMetadata with token details
        """
        # This is a stub - actual implementation would query GitHub API
        # Example: GET /user/tokens/{token_id}
        
        return SecretMetadata(
            secret_id=secret_id,
            secret_type=SecretType.TOKEN,
            provider=ProviderType.GITHUB,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=90),
            rotation_policy="auto_rotate_on_exposure",
            tags={"provider": "github", "type": "pat"},
            scopes=["repo", "workflow"]  # Example scopes
        )
    
    def get_expiration(self, secret_id: str) -> Optional[datetime]:
        """Get GitHub token expiration.
        
        Args:
            secret_id: Token ID
            
        Returns:
            Expiration datetime or None
        """
        try:
            metadata = self.get_secret_metadata(secret_id)
            return metadata.expires_at
        except Exception as e:
            logger.error(f"Failed to get token expiration: {e}")
            return None
    
    def get_scopes(self, secret_id: str) -> List[str]:
        """Get GitHub token scopes.
        
        Args:
            secret_id: Token ID
            
        Returns:
            List of scope strings
        """
        try:
            metadata = self.get_secret_metadata(secret_id)
            return metadata.scopes or []
        except Exception as e:
            logger.error(f"Failed to get token scopes: {e}")
            return []
    
    def create_token(
        self,
        name: str,
        scopes: List[str],
        expires_in_days: Optional[int] = None
    ) -> RotationResult:
        """Create new GitHub token.
        
        Args:
            name: Token description/note
            scopes: List of permissions
            expires_in_days: Days until expiration
            
        Returns:
            RotationResult with new token details
        """
        try:
            # This is a stub implementation; actual token creation must use the GitHub API.
            # For fine-grained PATs: POST /user/tokens
            # For classic PATs: Manual process or appropriate API flow when available.
            # TODO: Replace mock token generation below with real GitHub API integration.
            
            logger.info(f"Creating GitHub token: {_redact_identifier(name)}")
            
            # TODO: Remove this mock token ID and use the ID/value returned by GitHub instead.
            token_id = f"ghp_mock_{datetime.now(UTC).timestamp()}"
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=token_id,
                new_secret_value="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                metadata={
                    "name": name,
                    "scopes": scopes,
                    "expires_in_days": expires_in_days,
                    "created_at": datetime.now(UTC).isoformat(),
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create GitHub token: {e}")
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def update_token_scopes(
        self,
        secret_id: str,
        scopes: List[str]
    ) -> bool:
        """Update GitHub token scopes.
        
        For fine-grained PATs, updates permission set.
        For classic PATs, requires recreation.
        
        Args:
            secret_id: Token ID
            scopes: New list of scopes
            
        Returns:
            True if updated successfully
        """
        try:
            # This is a stub - actual implementation would use GitHub API
            # PATCH /user/tokens/{token_id}
            
            logger.info(f"Updating GitHub token scopes: {_redact_identifier(secret_id)}")
            logger.debug(f"New scopes: {scopes}")
            
            # TODO: Actual API call
            return True
            
        except Exception as e:
            logger.error(f"Failed to update token scopes: {e}")
            return False
    
    def revoke_secret(self, secret_id: str) -> bool:
        """Revoke GitHub token.
        
        Args:
            secret_id: Token ID to revoke
            
        Returns:
            True if revoked successfully
        """
        try:
            # This is a stub - actual implementation would use GitHub API
            # DELETE /user/tokens/{token_id}
            
            logger.info(f"Revoking GitHub token: {_redact_identifier(secret_id)}")
            
            # TODO: Actual API call
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            return False
    
    def list_secrets(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all GitHub tokens.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            # This is a stub - actual implementation would use GitHub API
            # GET /user/tokens
            
            logger.info("Listing GitHub tokens")
            
            # TODO: Actual API call
            return []
            
        except Exception as e:
            logger.error(f"Failed to list tokens: {e}")
            return []
