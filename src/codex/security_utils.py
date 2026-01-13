"""
Security utilities for handling sensitive information.
Provides redaction and sanitization functions to prevent
clear-text logging and storage of sensitive data.
"""

import re
from typing import Any, Dict, Optional


def redact_sensitive_value(value: str, show_preview: bool = False) -> str:
    """
    Redact a sensitive value for safe logging.
    
    Args:
        value: The sensitive value to redact
        show_preview: If True, show first/last 4 chars (for debugging only)
        
    Returns:
        Redacted string safe for logging
        
    Example:
        >>> redact_sensitive_value("my-secret-key-12345")
        '[REDACTED]'
        >>> redact_sensitive_value("my-secret-key-12345", show_preview=True)
        'my-s...[REDACTED]...2345'
    """
    if not value:
        return '[EMPTY]'
    
    if show_preview and len(value) > 8:
        return f"{value[:4]}...[REDACTED]...{value[-4:]}"
    
    return '[REDACTED]'


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
        'secret:CODEX_MASTER_KEY'
        >>> redact_secret_name("GOOGLE_CLIENT_SECRET")
        'secret:GOOGLE_CLIENT_SECRET'
    """
    if not secret_name:
        return '[UNNAMED_SECRET]'
    
    # For well-known configuration keys, we can use descriptive names
    # that don't reveal implementation details
    safe_prefixes = ['CODEX_', 'GITHUB_', 'GH_']
    
    # Check if this is a generally safe configuration name
    if any(secret_name.startswith(prefix) for prefix in safe_prefixes):
        return f"secret:{secret_name}"
    
    # For other secrets, provide minimal information
    return f"secret:[TYPE_{secret_name.split('_')[0] if '_' in secret_name else 'CUSTOM'}]"


def sanitize_log_message(message: str, redact_patterns: Optional[list] = None) -> str:
    """
    Sanitize a log message by redacting potential sensitive information.
    
    Args:
        message: The log message to sanitize
        redact_patterns: Optional list of regex patterns to redact
        
    Returns:
        Sanitized message safe for logging
        
    Example:
        >>> sanitize_log_message("Token: abc123def456")
        'Token: [REDACTED]'
    """
    # Default patterns for common sensitive data
    default_patterns = [
        (r'([A-Za-z0-9+/]{40,})', '[REDACTED_TOKEN]'),  # Long base64-like strings
        (r'(sk_[a-zA-Z0-9]{24,})', '[REDACTED_API_KEY]'),  # API keys
        (r'(ghp_[a-zA-Z0-9]{36,})', '[REDACTED_GITHUB_TOKEN]'),  # GitHub tokens
        (r'(gho_[a-zA-Z0-9]{36,})', '[REDACTED_OAUTH_TOKEN]'),  # OAuth tokens
    ]
    
    sanitized = message
    for pattern, replacement in default_patterns:
        sanitized = re.sub(pattern, replacement, sanitized)
    
    # Apply custom patterns if provided
    if redact_patterns:
        for pattern in redact_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
    
    return sanitized


def safe_secret_reference(secret_name: str, operation: str = "") -> str:
    """
    Create a safe reference to a secret for logging purposes.
    
    This function generates log-safe references that indicate
    a secret is being used without revealing sensitive details.
    
    Args:
        secret_name: Name of the secret
        operation: Optional operation being performed (e.g., 'set', 'verify')
        
    Returns:
        Safe reference string for logging
        
    Example:
        >>> safe_secret_reference("MASTER_KEY", "verify")
        'secret (verify)'
        >>> safe_secret_reference("API_TOKEN")
        'secret'
    """
    if operation:
        return f"secret ({operation})"
    return "secret"


# WARNING: Do NOT log secret names, values, or any sensitive credentials.
# Always use the redaction utilities above before logging.
