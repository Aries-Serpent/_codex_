"""
Security utilities for handling sensitive information.
Provides redaction and sanitization functions to prevent
clear-text logging and storage of sensitive data.
"""

import os
import re
from typing import Any, Optional


def redact_sensitive_value(value: Optional[str], show_preview: bool = False) -> str:
    """
    Redact a sensitive value for safe logging.

    Args:
        value: The sensitive value to redact (can be None)
        show_preview: If True, show first/last 4 chars (DEVELOPMENT/DEBUG ONLY - DO NOT USE IN PRODUCTION)

    Returns:
        Redacted string safe for logging

    Warning:
        The show_preview parameter should NEVER be enabled in production environments.
        It is intended solely for local development debugging. Using it in production
        would leak partial sensitive data.

        **PRODUCTION SAFETY**: This function checks the CODEX_ENV environment variable.
        If CODEX_ENV is set to 'production', 'prod', or 'prd', the show_preview parameter
        is automatically disabled regardless of its value.

    Example:
        >>> redact_sensitive_value("my-secret-key-12345")
        '[REDACTED]'
        >>> # DEV ONLY - DO NOT USE IN PRODUCTION
        >>> redact_sensitive_value("my-secret-key-12345", show_preview=True)
        'my-s...[REDACTED]...2345'
    """  # noqa: E501
    if not value:
        return "[EMPTY]"

    # Production safety: Explicitly disable show_preview in production environments
    # Check for production environment indicators
    codex_env = os.getenv("CODEX_ENV", "").lower()
    is_production = codex_env in ("production", "prod", "prd")

    # Additional safety checks for common production indicators
    if not is_production:
        # Check for other common production environment variables
        env_hints = os.getenv("ENVIRONMENT", "").lower()
        app_env = os.getenv("APP_ENV", "").lower()
        is_production = env_hints in ("production", "prod", "prd") or app_env in (
            "production",
            "prod",
            "prd",
        )

    # Override show_preview in production
    if is_production:
        show_preview = False

    # Production safety: show_preview should never be True in production
    # This parameter exists only for local development debugging
    if show_preview and len(value) > 8:
        return f"{value[:4]}...[REDACTED]...{value[-4:]}"

    return "[REDACTED]"


def redact_secret_name(secret_name: str) -> str:
    """
    Redact or sanitize a secret name for safe logging.

    Secret names themselves can sometimes reveal sensitive information
    about system architecture or credentials. This function provides
    safe logging of secret references.

    Args:
        secret_name: The name of the secret

    Returns:
        Sanitized secret reference safe for logging

    Example:
        >>> redact_secret_name("CODEX_MASTER_KEY")
        'secret:[REDACTED]'
        >>> redact_secret_name("CUSTOM_API_KEY")
        'secret:[REDACTED]'
    """
    if not secret_name:
        return "[UNNAMED_SECRET]"

    # Consistently redact all secret names to prevent information disclosure
    return "[REDACTED_SECRET_NAME]"


def sanitize_log_message(
    message: str,
    redact_patterns: Optional[list[Any]] = None,
    whitelist_patterns: Optional[list[Any]] = None,
) -> str:
    """
    Sanitize a log message by redacting potential sensitive information.

    Args:
        message: The log message to sanitize
        redact_patterns: Optional list of regex patterns to redact
        whitelist_patterns: Optional list of regex patterns for known-safe content to preserve
                            (e.g., common hash formats, UUIDs, etc.)

    Returns:
        Sanitized message safe for logging

    Note:
        Default patterns are designed to match known sensitive token formats.
        The base64 pattern is intentionally conservative (40+ chars) to minimize
        false positives while catching most tokens. Legitimate identifiers like
        UUIDs and short hashes (typically <36 chars) are not matched.

        Whitelist patterns allow you to protect known-safe content from redaction.
        For example, you might whitelist git commit SHAs, UUIDs, or specific hash formats.

    Example:
        >>> sanitize_log_message("Token: abc123def456")
        'Token: [REDACTED]'
        >>> # With whitelist to preserve commit SHAs
        >>> sanitize_log_message("Commit abc123, Token: ghp_realtoken", whitelist_patterns=[r'\\bCommit [a-f0-9]{6,40}\\b'])
        'Commit abc123, Token: [REDACTED_GITHUB_TOKEN]'
    """  # noqa: E501
    # Default patterns for common sensitive data
    # Note: These patterns are tuned to balance security with false positive rate
    default_patterns = [
        # GitHub personal access tokens (ghp_*) - 6+ alphanumeric chars
        (r"ghp_[a-zA-Z0-9]{6,}", "[REDACTED_GITHUB_TOKEN]"),
        # GitHub OAuth tokens (gho_*)
        (r"gho_[a-zA-Z0-9]{6,}", "[REDACTED_OAUTH_TOKEN]"),
        # Stripe/similar API keys (sk_live_*, sk_test_*) - with underscore
        (r"sk_(?:live|test)_[a-zA-Z0-9]{6,}", "[REDACTED]"),
        # Generic sk_ prefixed keys (underscore separator)
        (r"sk_[a-zA-Z0-9]{6,}", "[REDACTED]"),
        # Generic sk- prefixed keys (hyphen separator, e.g. OpenAI)
        (r"sk-[a-zA-Z0-9]{4,}", "[REDACTED]"),
        # AWS access keys (AKIA*, ASIA*)
        (r"A[KS]IA[A-Z0-9]{16}", "[REDACTED]"),
        # JWT tokens (three base64 segments separated by dots)
        (r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "[REDACTED]"),
        # Long base64-like strings (40+ chars) - catches tokens while avoiding short identifiers
        # This threshold balances security (catching tokens) with false positive reduction
        # Most legitimate short identifiers (UUIDs, SHAs) are <36 chars and whitelisted
        (r"[A-Za-z0-9+/]{40,}={0,2}", "[REDACTED_TOKEN]"),
    ]

    # Default whitelist patterns for common non-sensitive identifiers
    default_whitelist = [
        # UUID v4 (with or without hyphens)
        r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
        # UUID without hyphens (32 chars)
        r"\b[0-9a-f]{32}\b",
        # Git commit SHAs (40 hex chars or abbreviated 7-12 chars)
        r"\b[a-f0-9]{7,40}\b",
        # MD5 hashes (32 hex chars)
        r"\b[a-f0-9]{32}\b",
        # SHA-1 hashes (40 hex chars)
        r"\b[a-f0-9]{40}\b",
        # SHA-256 hashes (64 hex chars)
        r"\b[a-f0-9]{64}\b",
    ]

    # Build whitelist set
    whitelist = set(default_whitelist)
    if whitelist_patterns:
        whitelist.update(whitelist_patterns)

    # Temporarily mark whitelisted content to preserve it
    whitelist_placeholders: dict[str, Any] = {}
    temp_message = message
    for i, pattern in enumerate(whitelist):
        matches = re.finditer(pattern, temp_message, re.IGNORECASE)
        for match in matches:
            placeholder = f"__WHITELIST_{i}_{len(whitelist_placeholders)}__"
            whitelist_placeholders[placeholder] = match.group(0)
            temp_message = temp_message.replace(match.group(0), placeholder, 1)

    # Apply redaction patterns
    sanitized = temp_message
    for pattern, replacement in default_patterns:
        sanitized = re.sub(pattern, replacement, sanitized)

    # Apply custom patterns if provided
    if redact_patterns:
        for pattern in redact_patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized)

    # Restore whitelisted content
    for placeholder, original in whitelist_placeholders.items():
        sanitized = sanitized.replace(placeholder, original)

    return sanitized


def safe_secret_reference(name: str = "", operation: str = "") -> str:
    """
    Create a safe reference to a secret for logging purposes.

    This function generates log-safe references that indicate
    a secret is being used without revealing sensitive details.

    Args:
        name: Name of the secret (will be redacted if sensitive)
        operation: Optional operation being performed (e.g., 'set', 'verify')

    Returns:
        Safe reference string for logging

    Example:
        >>> safe_secret_reference("MY_API_KEY")
        'secret: MY_API_KEY'
        >>> safe_secret_reference("PROD_DATABASE_PASSWORD")
        '[REDACTED_SECRET_NAME]'
        >>> safe_secret_reference("verify", operation="check")
        'secret: verify'
        >>> safe_secret_reference("")
        '[EMPTY]'
    """
    if not name and not operation:
        return "[EMPTY]"
    if not name:
        return f"secret ({operation})"

    # Sensitive keyword check — redact names that reveal production secrets
    _SENSITIVE_KEYWORDS = (
        "PASSWORD",
        "SECRET",
        "PRIVATE_KEY",
        "PRIVATE",
        "CREDENTIAL",
        "DATABASE_URL",
        "DB_PASS",
        "ACCESS_KEY",
        "TOKEN",
    )
    name_upper = name.upper()
    if any(k in name_upper for k in _SENSITIVE_KEYWORDS):
        return "[REDACTED_SECRET_NAME]"

    if operation:
        return f"secret: {name} ({operation})"
    return f"secret: {name}"


def redact_dict_with_secret_keys(data: Optional[dict[str, Any]]) -> dict[str, Any]:
    """
    Redact a dictionary that uses secret names as keys.

    Args:
        data: Dictionary with potentially sensitive keys (can be None)

    Returns:
        Dictionary with redacted keys (indexed)

    Example:
        >>> redact_dict_with_secret_keys({"SECRET_1": "value", "SECRET_2": "value"})
        {"secret_1": "value", "secret_2": "value"}
    """
    if not data:
        return {}

    return {f"secret_{i + 1}": v for i, (k, v) in enumerate(data.items())}


# WARNING: Do NOT log secret names, values, or any sensitive credentials.
# Always use the redaction utilities above before logging.
