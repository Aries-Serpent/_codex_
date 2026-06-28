"""
Unified security utilities module for the Codex project.

This module consolidates security utilities from across the codebase,
providing a single import point for all security-related functions.

Key Features:
- Sensitive data masking (tokens, passwords, emails)
- Log injection prevention
- Secure hashing (SHA-256, SHA-512)
- Input sanitization

Usage:
    from codex.security import mask_token, sanitize_log, hash_secure

    # Mask sensitive data before logging
    logger.info(f"Token: {mask_token(api_key)}")

    # Sanitize user input to prevent log injection
    logger.info(f"User input: {sanitize_log(user_data)}")

    # Hash tokens securely for comparison
    token_hash = hash_secure(token)
"""

import hashlib
import re
from typing import Any, Optional
from urllib.parse import urlparse

# Re-export existing utilities from src/utils for backward compatibility
try:
    from utils.log_sanitizer import sanitize_dict_for_log, sanitize_log_input
    from utils.sensitive_data import mask_email, mask_password, mask_token
except ImportError:
    # Fallback implementations if imports fail
    def mask_token(token: str, show_last: int = 4) -> str:
        """Mask token showing only last N characters."""
        if not token:
            return "***"
        if len(token) <= show_last:
            return "*" * len(token)
        return "*" * (len(token) - show_last) + token[-show_last:]

    def mask_email(email: str) -> str:
        """Mask email preserving first char and domain."""
        if "@" not in email:
            return "***@***.***"
        user, domain = email.split("@", 1)
        return f"{user[0]}***@{domain}"

    def mask_password(password: str) -> str:
        """Always mask passwords completely."""
        return "***" if password else "(empty)"

    def sanitize_log_input(value: Any, max_length: int = 500) -> str:
        """Sanitize user input for safe logging."""
        if value is None:
            return "None"
        str_value = str(value)
        sanitized = re.sub(r"[\n\r\t\x00-\x1f\x7f-\x9f]", "", str_value)
        if len(sanitized) > max_length:
            return sanitized[:max_length] + "...[truncated]"
        return sanitized

    def sanitize_dict_for_log(data: dict[str, Any], max_length: int = 500) -> dict[str, Any]:
        """Sanitize dictionary values for safe logging."""
        return {k: sanitize_log_input(v, max_length) for k, v in data.items()}


def sanitize_log(value: Any, max_length: int = 500) -> str:
    """
    Alias for sanitize_log_input for consistency with module naming.

    Sanitizes user-controlled data for safe logging by removing control
    characters that could enable log injection attacks.

    Args:
        value: Value to sanitize (converted to string)
        max_length: Maximum output length (default: 500)

    Returns:
        Sanitized string safe for logging

    Example:
        >>> sanitize_log("user\\nfake_entry")
        'userfake_entry'
    """
    return sanitize_log_input(value, max_length)


def hash_secure(data: str, algorithm: str = "sha256") -> str:
    """
    Securely hash data using SHA-256 or SHA-512.

    Use this for hashing tokens, passwords, or other sensitive data
    for comparison purposes. Never use MD5 or SHA-1 for security.

    Args:
        data: String data to hash
        algorithm: Hash algorithm ('sha256' or 'sha512')

    Returns:
        Hexadecimal hash digest

    Example:
        >>> hash_secure("my_secret_token")
        'a1b2c3...'  # 64-character hex string for SHA-256

    Note:
        For password hashing, use specialized libraries like bcrypt,
        argon2, or scrypt instead of this function.
    """
    if algorithm == "sha256":
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    if algorithm == "sha512":
        return hashlib.sha512(data.encode("utf-8")).hexdigest()
    raise ValueError(f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'.")


def mask_sensitive(value: str, show_chars: int = 4) -> str:
    """
    Mask sensitive string showing first and last N characters.

    Useful for displaying partial values for verification while
    protecting the full secret.

    Args:
        value: Sensitive string to mask
        show_chars: Number of characters to show at start/end

    Returns:
        Masked string in format "xxxx***yyyy"

    Example:
        >>> mask_sensitive("secret_key_12345")
        'secr***12345'
        >>> mask_sensitive("short")
        '*****'
    """
    if not value:
        return ""
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    return f"{value[:show_chars]}***{value[-show_chars:]}"


def sanitize_url(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.

    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.

    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.

    Returns:
        True if URL is from an allowed domain, False otherwise

    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False

    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False

    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()

        # Remove port if present
        if ":" in netloc:
            netloc = netloc.split(":", 1)[0]

        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)

        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith("." + allowed_lower):
                return True

        return False
    except (ConnectionError, TimeoutError):
        # If URL parsing fails, consider it invalid
        return False


# Convenience re-exports for common use cases
__all__ = [
    # Masking functions
    "mask_token",
    "mask_email",
    "mask_password",
    "mask_sensitive",
    # Sanitization functions
    "sanitize_log",
    "sanitize_log_input",
    "sanitize_dict_for_log",
    "sanitize_url",
    # Hashing functions
    "hash_secure",
]
