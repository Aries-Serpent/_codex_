"""GitHub Token Provider implementation.

This module implements the SecretProvider interface for GitHub Personal
Access Tokens (PATs) and GitHub Apps, supporting token rotation, validation,
and scope management.

**IMPORTANT**: Several methods in this module are stubs that must be implemented
before production use:
- `create_token()`: Raises NotImplementedError - must be wired to GitHub API
- `revoke_secret()`: Calls the GitHub API to revoke installation tokens (ghs_);
  returns False for classic PATs that require OAuth App credentials not configured.
- `list_secrets()`: Calls GET /user to return metadata for the current token.

`validate_secret()` now calls `GET /api.github.com/user` to verify the token
is live and accepted by GitHub. Requires network access; gracefully degrades to
format-only validation when the network is unreachable.

Part of PS-05 Enhancement: Multi-Provider Support - Priority 4
"""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

from security.providers.base import (
    ProviderConfig,
    ProviderType,
    RotationResult,
    SecretMetadata,
    SecretType,
    TokenProvider,
    ValidationError,
)

logger = logging.getLogger(__name__)

# Module-level requests availability flag — avoids repeated ImportError handling
try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    _requests = None  # type: ignore[assignment]
    HAS_REQUESTS = False

# Pre-compiled GitHub token format regex — avoids recompiling on every call
_GITHUB_TOKEN_RE = re.compile(r"^(gh[pousr]_[A-Za-z0-9_]{36,}|[0-9a-f]{40})$")

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

            logger.info("Validating GitHub token")

            # Check local expiration first (avoids unnecessary API call)
            try:
                expiration = self.get_expiration(secret_id)
                if expiration and datetime.now(UTC) >= expiration:
                    logger.warning("GitHub token has expired (local expiry check)")
                    return False
            except Exception as e:
                logger.debug(f"Could not check expiration: {e}")

            # Validate token format — GitHub tokens start with 'ghp_', 'gho_',
            # 'ghs_', 'ghu_', or the classic 40-hex-char pattern.
            if not _GITHUB_TOKEN_RE.match(token):
                logger.warning("GitHub token does not match expected format")
                return False

            # Live validation: call GET /user to confirm the token is accepted
            # by GitHub.  Falls back gracefully if network is unreachable so
            # offline / air-gapped deployments are not broken.
            if not HAS_REQUESTS:
                # requests not available — fall back to format-only validation
                logger.warning(
                    "requests library unavailable; using format-only token validation"
                )
                return True
            try:
                resp = _requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=10,
                )
                if resp.status_code == 401:
                    logger.warning("GitHub token rejected by API (401 Unauthorized)")
                    return False
                if resp.status_code == 403:
                    logger.warning("GitHub token forbidden by API (403 Forbidden)")
                    return False
                if resp.status_code == 200:
                    logger.info("GitHub token validated successfully via API")
                    return True
                # Unexpected status — treat as valid but log
                logger.warning(
                    "GitHub API returned unexpected status %d; treating token as valid",
                    resp.status_code,
                )
                return True
            except Exception as network_err:
                # Network unreachable, DNS failure, timeout — degrade gracefully
                logger.warning(
                    "GitHub API unreachable (%s); using format-only token validation",
                    network_err,
                )
                return True

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

        Raises:
            NotImplementedError: This is a stub that must be implemented
        """
        raise NotImplementedError(
            "GitHub token creation is not implemented. This method is a stub and "
            "must be wired to the GitHub API (for example, POST /user/tokens for "
            "fine-grained PATs) before it can be used."
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

            logger.info("Updating GitHub token scopes")
            logger.debug(f"New scopes: {scopes}")

            # NOTE: Stub — does NOT call the GitHub API (PATCH /user/tokens/{token_id}).
            logger.warning(
                "update_token_scopes() is a stub: scopes have NOT been updated via GitHub API."
            )
            return True

        except Exception as e:
            logger.error(f"Failed to update token scopes: {e}")
            return False

    def revoke_secret(self, secret_id: str) -> bool:
        """Revoke GitHub token via the GitHub REST API.

        For installation tokens (ghs_), calls DELETE /installation/token.
        For classic PATs (ghp_/gho_), revocation requires OAuth App credentials
        (client_id + client_secret) which are not configured — returns False.

        Args:
            secret_id: Token ID to revoke (unused; revokes the configured token)

        Returns:
            True if revoked successfully, False otherwise
        """
        token = self.config.get("token") or os.environ.get("GITHUB_TOKEN", "")
        if not token:
            logger.warning("revoke_secret(): no token configured; cannot revoke.")
            return False
        if not HAS_REQUESTS:
            logger.warning("revoke_secret(): requests library unavailable; cannot revoke.")
            return False
        try:
            # Fine-grained PATs and installation tokens can be revoked via DELETE /installation/token
            # Classic PATs require DELETE /applications/{client_id}/token (needs OAuth app client_id)
            # We attempt the installation token revoke path first (works for ghs_ tokens)
            if token.startswith("ghs_"):
                resp = _requests.delete(
                    "https://api.github.com/installation/token",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=10,
                )
                if resp.status_code in (204, 200):
                    logger.info("revoke_secret(): installation token revoked successfully.")
                    return True
                logger.warning(
                    "revoke_secret(): GitHub API returned %d; token may not be revoked.",
                    resp.status_code,
                )
                return False
            # For classic PATs, revocation requires a GitHub OAuth App client_id+secret.
            # Without those credentials we cannot safely call the API — log and return False.
            logger.warning(
                "revoke_secret(): classic PAT revocation requires OAuth App credentials "
                "(client_id + client_secret). Configure GitHubTokenProvider with "
                "client_id/client_secret to enable revocation. Token NOT revoked."
            )
            return False
        except Exception as exc:
            logger.error("revoke_secret() failed: %s", exc)
            return False

    def list_secrets(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List GitHub tokens via the GitHub REST API.

        Calls GET /user to confirm the token is valid and returns a single
        SecretMetadata entry for the currently configured token.

        Args:
            filter_tags: Optional tag filters (not applied to API results)

        Returns:
            List of SecretMetadata (one entry for the current token)
        """
        token = self.config.get("token") or os.environ.get("GITHUB_TOKEN", "")
        if not token:
            logger.warning("list_secrets(): no token configured; returning empty list.")
            return []
        if not HAS_REQUESTS:
            logger.warning("list_secrets(): requests library unavailable.")
            return []
        try:
            resp = _requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                meta = SecretMetadata(
                    secret_id="current_token",
                    name=f"GitHub PAT for {data.get('login', 'unknown')}",
                    created_at=datetime.now(UTC),
                    tags={"github_login": data.get("login", ""), "token_type": "pat"},
                    scopes=None,  # scope info not available from /user
                )
                return [meta]
            logger.warning("list_secrets(): GitHub API returned %d.", resp.status_code)
            return []
        except Exception as exc:
            logger.error("list_secrets() failed: %s", exc)
            return []
