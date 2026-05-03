"""
Utilities for handling sensitive data safely in logs and outputs.

This module provides functions to mask or hash sensitive information
(API keys, tokens, passwords, emails) before logging or displaying.

Security Rationale:
-------------------
Logging sensitive data in clear-text can lead to:
- Credential theft from log files
- Compliance violations (PCI-DSS, GDPR, etc.)
- Unauthorized access if logs are compromised

Always mask sensitive values before logging.

Example:
    >>> from src.utils.sensitive_data import mask_token
    >>> logger.info(f"Processing token: {mask_token(api_token)}")
"""

import hashlib
import re


def mask_token(token: str, show_last: int = 4) -> str:
    """
    Mask API token/key showing only last N characters.

    Args:
        token: Token or API key to mask
        show_last: Number of characters to show at the end (default: 4)

    Returns:
        Masked token string

    Example:
        >>> mask_token("sk_live_abc123xyz789")
        '****************xyz789'
        >>> mask_token("short", show_last=4)
        '*****'
    """
    if not token:
        return "***"
    if len(token) <= show_last:
        return "*" * len(token)
    return "*" * (len(token) - show_last) + token[-show_last:]


def mask_email(email: str) -> str:
    """
    Mask email address preserving first character and domain.

    Args:
        email: Email address to mask

    Returns:
        Masked email string

    Example:
        >>> mask_email("user@example.com")
        'u***@example.com'
        >>> mask_email("admin@company.org")
        'a***@company.org'
    """
    if not email or "@" not in email:
        return "***"
    user, domain = email.split("@", 1)
    if len(user) == 0:
        return f"***@{domain}"
    return f"{user[0]}***@{domain}"


def mask_password(password: str) -> str:
    """
    Completely mask password (don't show any characters).

    Args:
        password: Password to mask

    Returns:
        Fixed mask string. Returns a distinct marker for empty passwords
        to aid debugging while not exposing actual password values.

    Example:
        >>> mask_password("mySecretP@ssw0rd")
        '***'
        >>> mask_password("")
        '(empty)'
    """
    if password:
        # Non-empty password: return fixed mask to avoid leaking length or content
        return "***"
    # Empty or missing password: use a distinct marker to aid debugging
    return "(empty)"


def hash_for_logging(sensitive_value: str, prefix: str = "") -> str:
    """
    Create safe hash of sensitive value for logging/comparison.

    Use this when you need to log something for debugging purposes
    but it contains sensitive data. The hash can be used to:
    - Track the same value across logs without revealing it
    - Debug issues while maintaining security

    Args:
        sensitive_value: Sensitive data to hash
        prefix: Optional prefix for the hash (e.g., "pwd_hash")

    Returns:
        Hex hash string (first 16 chars of SHA-256)

    Example:
        >>> hash_for_logging("myPassword123", "pwd")
        'pwd:a1b2c3d4e5f67890'
    """
    if not sensitive_value:
        return f"{prefix}:***" if prefix else "***"

    hash_value = hashlib.sha256(sensitive_value.encode()).hexdigest()[:16]
    return f"{prefix}:{hash_value}" if prefix else hash_value


def mask_sensitive_dict(data: dict) -> dict:
    """
    Mask known sensitive keys in a dictionary.

    Automatically masks values for common sensitive key names:
    - password, passwd, pwd
    - token, api_key, apikey, secret
    - authorization, auth

    Args:
        data: Dictionary potentially containing sensitive data

    Returns:
        New dictionary with sensitive values masked

    Example:
        >>> mask_sensitive_dict({"user": "john", "password": "secret123"})
        {'user': 'john', 'password': '***'}
    """
    sensitive_keys = {
        "password",
        "passwd",
        "pwd",
        "token",
        "api_key",
        "apikey",
        "secret",
        "api_token",
        "authorization",
        "auth",
        "bearer",
        "private_key",
        "privatekey",
    }

    result = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(sens_key in key_lower for sens_key in sensitive_keys):
            # Sensitive key - mask the value
            if isinstance(value, str):
                result[key] = (
                    mask_token(value) if "token" in key_lower or "key" in key_lower else "***"
                )
            else:
                result[key] = "***"
        else:
            result[key] = value

    return result


def mask_sensitive_data(text: str) -> str:
    """Mask multiple types of sensitive data in text.

    Detects and masks:
    - Email addresses
    - Phone numbers (US format)
    - Social Security Numbers (SSN)
    - Credit card numbers
    - API keys (sk_*/pk_* format)
    - Passwords in assignments

    Args:
        text: Text potentially containing sensitive data

    Returns:
        Text with sensitive data masked

    Example:
        >>> mask_sensitive_data("Contact user@example.com or call 555-123-4567")
        'Contact u***@example.com or call ***-***-****'
    """
    if not text:
        return text

    # Email pattern
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        lambda m: mask_email(m.group()),
        text,
    )

    # Phone patterns (US format: XXX-XXX-XXXX, XXX.XXX.XXXX, XXXXXXXXXX, XXX-XXXX)
    text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "***-***-****", text)
    text = re.sub(r"\b\d{3}[-.]?\d{4}\b", "***-****", text)

    # SSN pattern (XXX-XX-XXXX)
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "***-**-****", text)

    # Credit card pattern (with or without dashes/spaces)
    text = re.sub(
        r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "****-****-****-****",
        text,
    )

    # API key pattern (sk_*, pk_* style keys with various formats)
    text = re.sub(r"\b(sk|pk)_[a-z]+_[A-Za-z0-9]{8,}\b", "***_REDACTED_***", text)

    # Password in quotes/assignments (password="value" or password: "value")
    return re.sub(
        r'(password|passwd|pwd|secret)\s*[=:]\s*["\']([^"\']+)["\']',
        r'\1="***"',
        text,
        flags=re.IGNORECASE,
    )


def hash_sensitive_value(value: str) -> str:
    """Create consistent hash of sensitive value for logging/comparison.

    This is a convenience wrapper around hash_for_logging() to match
    the test interface expectations.

    Args:
        value: Sensitive data to hash

    Returns:
        Hex hash string (first 16 chars of SHA-256)

    Example:
        >>> hash_sensitive_value("myPassword123")
        'a1b2c3d4e5f67890'
    """
    return hash_for_logging(value)


__all__ = [
    "hash_for_logging",
    "hash_sensitive_value",
    "mask_email",
    "mask_password",
    "mask_sensitive_data",
    "mask_sensitive_dict",
    "mask_token",
]
