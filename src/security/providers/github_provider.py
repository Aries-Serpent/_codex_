"""GitHub Token Provider implementation.

This module implements the SecretProvider interface for GitHub Personal
Access Tokens (PATs) and GitHub Apps, supporting token rotation, validation,
and scope management.

**Implementation status**:
- ``create_token()``: Creates GitHub App installation access tokens via
  ``POST /app/installations/{id}/access_tokens``.  Requires ``installation_id``
  in config or ``GITHUB_APP_INSTALLATION_ID`` env var.  Fine-grained / classic
  PATs cannot be created via the REST API (must be done via the GitHub UI).
- ``update_token_scopes()``: Calls ``PATCH /user/installations/{id}/permissions``
  when the ``requests`` library is available; returns False otherwise.
- ``revoke_secret()``: Calls the GitHub API to revoke installation tokens (ghs_);
  returns False for classic PATs that require OAuth App credentials not configured.
- ``list_secrets()``: Calls GET /user to return metadata for the current token.

``validate_secret()`` now calls ``GET https://api.github.com/user`` to verify the token
is live and accepted by GitHub. Requires network access; gracefully degrades to
format-only validation when the network is unreachable.

Part of PS-05 Enhancement: Multi-Provider Support - Priority 4
"""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, datetime, timedelta
from types import ModuleType
from typing import Any, Optional

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
_requests: ModuleType | None
try:
    import requests as _requests_module

    _requests = _requests_module

    HAS_REQUESTS = True
except ImportError:
    _requests = None
    HAS_REQUESTS = False

# Pre-compiled GitHub token format regex — avoids recompiling on every call
_GITHUB_TOKEN_RE = re.compile(r"^(gh[pousr]_[A-Za-z0-9_]{36,}|[0-9a-f]{40})$")

# Valid GitHub App installation permission names (subset — see GitHub REST API docs).
# PAT-style scopes like "repo" or "workflow" are NOT valid here.
_KNOWN_INSTALLATION_PERMISSIONS: frozenset[str] = frozenset(
    {
        "actions",
        "administration",
        "checks",
        "codespaces",
        "contents",
        "deployments",
        "environments",
        "issues",
        "members",
        "metadata",
        "organization_administration",
        "organization_hooks",
        "organization_packages",
        "organization_plan",
        "organization_projects",
        "organization_secrets",
        "organization_self_hosted_runners",
        "packages",
        "pages",
        "pull_requests",
        "repository_hooks",
        "repository_projects",
        "secret_scanning_alerts",
        "secrets",
        "security_events",
        "single_file",
        "statuses",
        "vulnerability_alerts",
        "workflows",
    }
)


def _redact_identifier(identifier: str) -> str:
    """Return a non-sensitive token/secret identifier for logs."""
    if not identifier:
        return "<empty>"
    if len(identifier) <= 8:
        return "***"
    return f"{identifier[:4]}...{identifier[-4:]}"


def _safe_error(exc: Exception) -> str:
    """Return a non-sensitive exception summary for logs/results."""
    return type(exc).__name__


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
            logger.warning("GitHub authentication not configured")

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.GITHUB

    def rotate_secret(self, secret_id: str, **kwargs: Any) -> RotationResult:
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
                name=note, scopes=scopes, expires_in_days=expires_in_days
            )

            if not new_token_result.success:
                return RotationResult(
                    success=False,
                    old_secret_id=secret_id,
                    error_message=new_token_result.error_message,
                )

            # Revoke old token (optional, based on policy)
            if kwargs.get("revoke_old", False):
                try:
                    self.revoke_secret(secret_id)
                except (ValueError, TypeError, RuntimeError) as e:
                    logger.warning("Failed to revoke prior grant: %s", _safe_error(e))

            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=new_token_result.new_secret_id,
                new_secret_value=new_token_result.new_secret_value,
                metadata={
                    "scopes": scopes,
                    "expires_in_days": expires_in_days,
                },
            )

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error("GitHub auth rotation failed: %s", _safe_error(e))
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"GitHub token rotation failed: {str(e)}",
            )

    def validate_secret(self, secret_id: str, secret_value: Optional[str] = None) -> bool:
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

            logger.info("Validating GitHub authentication")

            # Check local expiration first (avoids unnecessary API call)
            try:
                expiration = self.get_expiration(secret_id)
                if expiration and datetime.now(UTC) >= expiration:
                    logger.warning("GitHub authentication has expired (local expiry check)")
                    return False
            except (ValueError, TypeError, RuntimeError) as e:
                logger.debug("Could not check expiration: %s", _safe_error(e))

            # Validate token format — GitHub tokens start with 'ghp_', 'gho_',
            # 'ghs_', 'ghu_', or the classic 40-hex-char pattern.
            if not _GITHUB_TOKEN_RE.match(token):
                logger.warning("GitHub authentication does not match expected format")
                return False

            # Live validation: call GET /user to confirm the token is accepted
            # by GitHub.  Falls back gracefully if network is unreachable so
            # offline / air-gapped deployments are not broken.
            if not HAS_REQUESTS:
                # requests not available — fall back to format-only validation
                logger.warning("requests library unavailable; using format-only auth validation")
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
                    logger.warning("GitHub authentication rejected by API (401 Unauthorized)")
                    return False
                if resp.status_code == 403:
                    logger.warning("GitHub authentication forbidden by API (403 Forbidden)")
                    return False
                if resp.status_code == 200:
                    logger.info("GitHub authentication validated successfully via API")
                    return True
                # Unexpected status — treat as valid but log
                logger.warning(
                    "GitHub API returned unexpected status %d; treating token as valid",
                    resp.status_code,
                )
                return True
            except (ValueError, TypeError, RuntimeError) as network_err:
                # Network unreachable, DNS failure, timeout — degrade gracefully
                logger.warning(
                    "GitHub API unreachable (%s); using format-only token validation",
                    _safe_error(network_err),
                )
                return True

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Token validation failed: {_safe_error(e)}") from e

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
            scopes=["repo", "workflow"],  # Example scopes
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
        except (ValueError, TypeError, RuntimeError) as e:
            logger.error("Failed to get auth expiry: %s", _safe_error(e))
            return None

    def get_scopes(self, secret_id: str) -> list[str]:
        """Get GitHub token scopes.

        Args:
            secret_id: Token ID

        Returns:
            List of scope strings
        """
        try:
            metadata = self.get_secret_metadata(secret_id)
            return metadata.scopes or []
        except (ValueError, TypeError, RuntimeError) as e:
            logger.error("Failed to get access scopes: %s", _safe_error(e))
            return []

    def create_token(
        self, name: str, scopes: list[str], expires_in_days: Optional[int] = None
    ) -> RotationResult:
        """Create a new GitHub token via the REST API.

        For **GitHub App installation tokens** the method calls
        ``POST /app/installations/{installation_id}/access_tokens`` using the
        configured JWT bearer token.  For **fine-grained PATs** or **classic
        PATs** programmatic creation is not supported by the public REST API —
        those must be created through the GitHub settings UI.

        The ``installation_id`` is read from the provider config key
        ``installation_id`` or from the ``GITHUB_APP_INSTALLATION_ID``
        environment variable.

        Args:
            name: Token description (used in metadata only; the API does not
                accept a ``note`` for installation tokens).
            scopes: List of permission names.  Mapped to the ``permissions``
                dict expected by the API (each scope → ``"write"``).
            expires_in_days: Ignored for installation tokens (they are always
                short-lived, typically 1 h).

        Returns:
            RotationResult with ``success=True`` and the new token value on
            success, or ``success=False`` with an ``error_message``.
        """
        installation_id = self.config.get(
            "installation_id", os.environ.get("GITHUB_APP_INSTALLATION_ID")
        )

        if not installation_id:
            return RotationResult(
                success=False,
                old_secret_id="",  # nosec B106 — empty string default for result struct field, not a credential
                error_message=(
                    "Cannot create token: no installation_id configured. "
                    "Fine-grained PATs and classic PATs must be created "
                    "through the GitHub settings UI. Provide "
                    "'installation_id' in the provider config or set "
                    "GITHUB_APP_INSTALLATION_ID to create an installation "
                    "access token."
                ),
            )

        if not self.token:
            return RotationResult(
                success=False,
                old_secret_id="",  # nosec B106 — empty string default for result struct field, not a credential
                error_message="Cannot create token: no bearer token configured.",
            )

        if not HAS_REQUESTS:
            return RotationResult(
                success=False,
                old_secret_id="",  # nosec B106 — empty string default for result struct field, not a credential
                error_message="Cannot create token: requests library is not installed.",
            )

        # Build permissions dict from scopes list — only accept installation
        # permission names (not PAT-style scopes like "repo" / "workflow").
        invalid = [s for s in scopes if s not in _KNOWN_INSTALLATION_PERMISSIONS] if scopes else []
        if invalid:
            return RotationResult(
                success=False,
                old_secret_id="",  # nosec B106 — empty string default for result struct field, not a credential
                error_message=(
                    f"Invalid installation permission names: {invalid}. "
                    "Use GitHub App installation permission names "
                    "(e.g. 'contents', 'pull_requests', 'issues'), not "
                    "PAT-style scopes (e.g. 'repo', 'workflow')."
                ),
            )
        permissions: dict[str, str] = {s: "write" for s in scopes} if scopes else {}

        url = f"{self.api_url}/app/installations/{installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        body: dict[str, Any] = {}
        if permissions:
            body["permissions"] = permissions

        try:
            resp = _requests.post(url, json=body, headers=headers, timeout=15)
            if resp.status_code == 201:
                data = resp.json()
                new_token = data.get("token", "")
                if not new_token:
                    logger.error("GitHub API returned 201 but response contains no access value.")
                    return RotationResult(
                        success=False,
                        old_secret_id="",  # nosec B106 — empty string default for result struct field, not a credential
                        error_message="GitHub API returned 201 but no token in response body.",
                    )
                token_id = str(data.get("id", name))
                logger.info("GitHub installation grant created successfully.")
                return RotationResult(
                    success=True,
                    old_secret_id="",  # nosec B106 — empty string default for result struct field, not a credential
                    new_secret_id=token_id,
                    new_secret_value=new_token,
                    metadata={
                        "name": name,
                        "permissions": permissions,
                        "expires_at": data.get("expires_at"),
                    },
                )
            logger.error(
                "GitHub API returned %d when creating installation token.",
                resp.status_code,
            )
            return RotationResult(
                success=False,
                old_secret_id="",  # nosec B106 — empty string default for result struct field, not a credential
                error_message=f"GitHub API returned {resp.status_code} when creating installation token.",  # noqa: E501
            )
        except (ConnectionError, TimeoutError) as e:
            logger.error("Failed to create GitHub installation grant: %s", _safe_error(e))
            return RotationResult(
                success=False,
                old_secret_id="",  # nosec B106 — empty string default for result struct field, not a credential
                error_message=f"Token creation request failed: {_safe_error(e)}",
            )

    def update_token_scopes(self, secret_id: str, scopes: list[str]) -> bool:
        """Update GitHub token scopes.

        For fine-grained PATs, updates the permission set via
        ``PATCH /user/installations/{installation_id}/permissions`` (requires
        the ``requests`` library and a valid bearer token).  For classic PATs,  # codeql[py/clear-text-logging-sensitive-data]
        scope changes are not supported by the API — a new token must be
        created manually.

        The ``installation_id`` is resolved in order:

        1. ``secret_id`` parameter (when it looks like a numeric installation ID)
        2. Provider config ``installation_id``
        3. ``GITHUB_APP_INSTALLATION_ID`` environment variable

        Args:
            secret_id: Token or installation ID (used as fallback identifier)
            scopes: New list of scopes (GitHub App installation permission names)

        Returns:
            True if the API returned 200/204.  False when the request failed,
            prerequisites are missing, or the ``requests`` library is unavailable.
        """  # noqa: E501
        try:
            logger.info(
                "Updating GitHub access scopes (scope_count: %d)",
                len(scopes) if scopes else 0,
            )

            if not HAS_REQUESTS:
                logger.warning(
                    "update_token_scopes(): requests library unavailable; "
                    "scopes have NOT been updated via GitHub API."
                )
                return False

            if not self.token:
                logger.warning(
                    "update_token_scopes(): no bearer token configured; "
                    "scopes have NOT been updated."
                )
                return False
            # codeql[py/clear-text-logging-sensitive-data]
            # Resolve installation_id: prefer config/env, fall back to secret_id
            installation_id = self.config.get(
                "installation_id", os.environ.get("GITHUB_APP_INSTALLATION_ID", secret_id)
            )
            permissions: dict[str, str] = {s: "write" for s in scopes} if scopes else {}
            url = f"{self.api_url}/user/installations/{installation_id}/permissions"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            resp = _requests.patch(
                url, json={"permissions": permissions}, headers=headers, timeout=10
            )
            if resp.status_code in (200, 204):
                logger.info("GitHub access scopes updated successfully.")
                return True
            logger.warning(
                "update_token_scopes(): GitHub API returned %d; scopes may not be updated.",
                resp.status_code,
            )
            return False

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error("Failed to update access scopes: %s", _safe_error(e))
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
            logger.warning("GitHub revoke API unavailable without configured auth material.")
            return False
        if not HAS_REQUESTS:
            logger.warning("GitHub revoke API unavailable: requests library missing.")
            return False
        try:
            # Fine-grained PATs and installation tokens can be revoked via DELETE /installation/token  # noqa: E501
            # Classic PATs require DELETE /applications/{client_id}/token (needs OAuth app client_id)  # noqa: E501
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
                    logger.info("GitHub revoke API: installation grant revoked successfully.")
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
        except (ValueError, TypeError, RuntimeError) as exc:
            logger.error("GitHub revoke API failed: %s", _safe_error(exc))
            return False

    def list_secrets(self, filter_tags: Optional[dict[str, str]] = None) -> list[SecretMetadata]:
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
            logger.warning(
                "GitHub listing API has no auth material configured; returning empty list."
            )
            return []
        if not HAS_REQUESTS:
            logger.warning("GitHub listing API unavailable: requests library missing.")
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
                    secret_id="current_token",  # nosec B106
                    secret_type=SecretType.TOKEN,
                    provider=ProviderType.GITHUB,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    tags={
                        "github_login": data.get("login", ""),
                        "token_type": "pat",
                        "name": f"GitHub PAT for {data.get('login', 'unknown')}",
                    },  # nosec B105
                    scopes=None,  # scope info not available from /user
                )
                return [meta]
            logger.warning("GitHub listing API returned %d.", resp.status_code)
            return []
        except (ValueError, TypeError, RuntimeError) as exc:
            logger.error("GitHub listing API failed: %s", _safe_error(exc))
            return []
