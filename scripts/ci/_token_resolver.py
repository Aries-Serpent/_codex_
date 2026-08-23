"""Canonical token utility library for centralized token resolution.

This module provides a unified interface for token discovery, validation, and
scope checking across all scripts in the codebase. It eliminates code duplication
and ensures consistent token resolution patterns.

Example:
    >>> from scripts.ci._token_resolver import get_token, get_auth_header
    >>> token, source = get_token(required_elevated=True)
    >>> print(f"Using token from: {source}")
    >>> header = get_auth_header(token)
"""

import logging
import os
from typing import List, Optional, Tuple

# Environment variable hierarchy for token resolution
CANONICAL_HIERARCHY: List[str] = [
    "CODEX_MASTER_KEY",
    "CODEX_BACKUP_KEY",
    "GH_TOKEN",
    "GITHUB_TOKEN",
]

# Token scope mappings
TOKEN_SCOPES = {
    "CODEX_MASTER_KEY": [
        "repo",
        "workflow",
        "actions:write",
        "security_events",
        "admin:org_hook",
    ],
    "CODEX_BACKUP_KEY": ["repo", "workflow"],
    "GH_TOKEN": ["repo"],
    "GITHUB_TOKEN": ["repo"],
}

# Configure logging
logger = logging.getLogger(__name__)


class TokenResolutionError(Exception):
    """Raised when no suitable token is available or scope validation fails."""

    pass


def validate_token(token: str) -> Tuple[bool, str]:
    """Validate that a token exists and is not empty.

    Args:
        token: The token string to validate.

    Returns:
        Tuple of (is_valid, message) where is_valid is True if token is valid.

    Raises:
        None
    """
    if not token or not isinstance(token, str):
        return False, "Token must be a non-empty string"
    if len(token.strip()) == 0:
        return False, "Token cannot be empty or whitespace-only"
    return True, "Token is valid"


def get_token_source() -> str:
    """Return the name of the environment variable providing the current token.

    Scans CANONICAL_HIERARCHY in order and returns the name of the first
    available token source found.

    Returns:
        String name of the token source (e.g., "CODEX_MASTER_KEY")

    Raises:
        TokenResolutionError: If no token source is available.
    """
    for env_var in CANONICAL_HIERARCHY:
        if os.environ.get(env_var):
            return env_var
    raise TokenResolutionError(
        "No token available. Please set one of: "
        + ", ".join(CANONICAL_HIERARCHY[:2])
    )


def get_token(required_elevated: bool = False) -> Tuple[Optional[str], str]:
    """Return the best available token with validation.

    Scans environment variables in CANONICAL_HIERARCHY order and returns
    the first available token. If required_elevated is True, github.token
    (insufficient scope) will not be returned.

    Args:
        required_elevated: If True, only tokens with elevated scope are returned.
                          This excludes GH_TOKEN and GITHUB_TOKEN variants.

    Returns:
        Tuple of (token_value, token_source_name)

    Raises:
        TokenResolutionError: If no suitable token is available.
    """
    # Determine which sources are acceptable
    acceptable_sources = CANONICAL_HIERARCHY
    if required_elevated:
        acceptable_sources = CANONICAL_HIERARCHY[:2]  # Only CODEX keys

    # Scan hierarchy
    for env_var in acceptable_sources:
        token = os.environ.get(env_var)
        if token:
            is_valid, msg = validate_token(token)
            if is_valid:
                return token, env_var

    # No token found
    if required_elevated:
        raise TokenResolutionError(
            "No elevated token available. Required scopes: "
            "repo, workflow, actions:write, security_events. "
            "Please set CODEX_MASTER_KEY or CODEX_BACKUP_KEY."
        )
    else:
        raise TokenResolutionError(
            "No token available. Please set one of: "
            + ", ".join(CANONICAL_HIERARCHY)
        )


def _source_for_token(token: Optional[str]) -> Optional[str]:
    """Return the env var name that currently owns *token* if it is present.

    This keeps token scope checks tied to the actual token value rather than
    whichever source happens to be active in the environment.
    """
    if not isinstance(token, str):
        return None
    token = token.strip()
    if not token:
        return None
    for env_var in CANONICAL_HIERARCHY:
        candidate = os.environ.get(env_var)
        if candidate == token:
            return env_var
    return None


def get_token_scope(token: Optional[str] = None) -> str:
    """Return the detected scope level of the token.

    Determines scope level based on which environment variable the token
    came from. This is a static determination, not an API call.

    Args:
        token: Optional token to check. If not provided, uses current token.

    Returns:
        String scope level: "elevated", "standard", or "fallback"
        - elevated: CODEX_MASTER_KEY (repo + workflow + actions:write + security_events)
        - standard: CODEX_BACKUP_KEY (repo + workflow) or explicit github.token
        - fallback: GITHUB_TOKEN (limited scopes)

    Raises:
        TokenResolutionError: If token cannot be determined and none provided.
    """
    if token is None:
        try:
            token, source = get_token()
        except TokenResolutionError:
            return "fallback"
    else:
        source = _source_for_token(token)
        if source is None:
            try:
                _, source = get_token(required_elevated=False)
            except TokenResolutionError:
                return "fallback"

    if source == "CODEX_MASTER_KEY":
        return "elevated"
    if source == "CODEX_BACKUP_KEY":
        return "standard"
    if source in {"GH_TOKEN", "GITHUB_TOKEN"}:
        return "standard"
    return "fallback"


def validate_token_scope(
    token: Optional[str], required_scopes: List[str]
) -> Tuple[bool, str]:
    """Validate that a token has the required scopes.

    Determines required scopes based on the token source and compares with
    the provided required_scopes list. This is a static determination based
    on known scope mappings.

    Args:
        token: Token to validate. If None, uses current token source.
        required_scopes: List of required scope names.

    Returns:
        Tuple of (is_valid, message) where is_valid is True if scopes match.

    Raises:
        TokenResolutionError: If token source cannot be determined.
    """
    if token is None:
        try:
            token, source = get_token(required_elevated=False)
        except TokenResolutionError as e:
            return False, f"Cannot determine token source: {e}"
    else:
        source = _source_for_token(token)
        if source is None:
            try:
                _, source = get_token(required_elevated=False)
            except TokenResolutionError as e:
                return False, f"Cannot determine token source: {e}"

    available_scopes = TOKEN_SCOPES.get(source, ["repo"])
    missing_scopes = [s for s in required_scopes if s not in available_scopes]

    if missing_scopes:
        return (
            False,
            f"Token from {source} missing scopes: {', '.join(missing_scopes)}. "
            f"Available: {', '.join(available_scopes)}",
        )

    return True, f"Token from {source} has all required scopes"


def get_auth_header(token: Optional[str] = None) -> str:
    """Return a properly formatted Authorization header for API calls.

    Creates an Authorization header string suitable for use in HTTP requests
    to GitHub APIs. Falls back to current token if not provided.

    Args:
        token: Optional token to use. If not provided, uses current token.

    Returns:
        String "Authorization: token <token_value>" or error header if no token.

    Raises:
        TokenResolutionError: If no token available and none provided.
    """
    if token is None:
        token, _ = get_token()

    if not token:
        raise TokenResolutionError("No token available for Authorization header")

    return f"Authorization: token {token}"


def log_token_usage(context: str, required_elevated: bool = False) -> None:
    """Log which token is being used and why (with audit trail).

    Logs the token source and context for audit purposes. DOES NOT log the
    actual token value or any sensitive information.

    Args:
        context: Description of why token is being used (e.g., "Writing repo var").
        required_elevated: Whether elevated scope token is required.

    Returns:
        None

    Raises:
        TokenResolutionError: If no suitable token available.
    """
    try:
        token, source = get_token(required_elevated=required_elevated)
        scope = get_token_scope(token)
        logger.info(
            f"Using token: source={source}, scope={scope}, context={context}"
        )
    except TokenResolutionError as e:
        logger.error(f"Token resolution failed: {e}")
        raise


__all__ = [
    "CANONICAL_HIERARCHY",
    "get_token",
    "get_token_source",
    "get_token_scope",
    "validate_token_scope",
    "get_auth_header",
    "validate_token",
    "log_token_usage",
    "TokenResolutionError",
]
