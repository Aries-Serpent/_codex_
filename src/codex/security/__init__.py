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

# Re-export existing utilities from src/utils for backward compatibility
try:
    from src.utils.sensitive_data import mask_token, mask_email, mask_password
    from src.utils.log_sanitizer import sanitize_log_input, sanitize_dict_for_log
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
        sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
        if len(sanitized) > max_length:
            return sanitized[:max_length] + "...[truncated]"
        return sanitized
    
    def sanitize_dict_for_log(data: dict, max_length: int = 500) -> dict:
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


def hash_secure(data: str, algorithm: str = 'sha256') -> str:
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
    if algorithm == 'sha256':
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


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


# Convenience re-exports for common use cases
__all__ = [
    # Masking functions
    'mask_token',
    'mask_email', 
    'mask_password',
    'mask_sensitive',
    # Sanitization functions
    'sanitize_log',
    'sanitize_log_input',
    'sanitize_dict_for_log',
    # Hashing functions
    'hash_secure',
]
