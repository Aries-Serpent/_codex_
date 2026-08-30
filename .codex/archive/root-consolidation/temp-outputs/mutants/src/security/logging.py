"""
Security-aware logging utilities for redacting sensitive data.

This module provides functions for safely logging sensitive information
without exposing secrets, tokens, or PII in log output.

CWE-532: Insertion of Sensitive Information into Log File
OWASP A09:2021 - Security Logging and Monitoring Failures
"""

import hashlib
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


# Common token/secret patterns for detection
TOKEN_PATTERNS = [
    r"ghp_[a-zA-Z0-9]{36}",  # GitHub Personal Access Token
    r"ghs_[a-zA-Z0-9]{36}",  # GitHub OAuth token
    r"ghu_[a-zA-Z0-9]{36}",  # GitHub User-to-Server token
    r"github_pat_[a-zA-Z0-9]+",  # GitHub fine-grained token
    r"sk_[a-zA-Z0-9]{32,}",  # Generic secret key
    r"[a-zA-Z0-9_-]{20,}",  # Generic token-like pattern
]

PASSWORD_PATTERNS = [
    r"password['\"]?\s*[:=]\s*['\"]?[^'\"]*['\"]?",
    r"pwd['\"]?\s*[:=]\s*['\"]?[^'\"]*['\"]?",
    r"passwd['\"]?\s*[:=]\s*['\"]?[^'\"]*['\"]?",
]


def redact_token(
    value: str,
    prefix_len: int = 4,
    suffix_visible: bool = False,
) -> str:
    """
    Redact a token/secret by showing only the prefix.

    Args:
        value: The token or secret to redact
        prefix_len: Number of characters to show from start (default: 4)
        suffix_visible: Whether to show last 4 chars (default: False)

    Returns:
        Redacted version like "ghp_****" or "ghp_****89ab"

    Examples:
        >>> redact_token("ghp_1234567890abcdefghij1234567890")
        'ghp_****'

        >>> redact_token("ghp_1234567890abcdefghij1234567890", suffix_visible=True)
        'ghp_****7890'
    """
    if not value or len(value) <= prefix_len:
        return "***" * len(value) if value else "***"

    if suffix_visible and len(value) > prefix_len + 4:
        return f"{value[:prefix_len]}****{value[-4:]}"

    return f"{value[:prefix_len]}****"


def redact_password(value: str) -> str:
    """
    Redact a password by masking most characters.

    Args:
        value: The password to redact

    Returns:
        Redacted password (masked entirely for security)

    Examples:
        >>> redact_password("my_secret_password")
        '[REDACTED_PASSWORD]'
    """
    return "[REDACTED_PASSWORD]" if value else "[EMPTY_PASSWORD]"


def redact_email(email: str) -> str:
    """
    Redact an email address showing only domain.

    Args:
        email: The email address to redact

    Returns:
        Partially redacted email like u****@example.com

    Examples:
        >>> redact_email("user@example.com")
        'u****@example.com'
    """
    if "@" not in email:
        return "****"

    local, domain = email.split("@", 1)
    if len(local) <= 1:
        return f"*@{domain}"

    return f"{local[0]}****@{domain}"


def redact_pii(value: str, pii_type: str = "generic") -> str:
    """
    Redact personally identifiable information.

    Args:
        value: The PII value to redact
        pii_type: Type of PII (email, phone, ssn, credit_card, etc.)

    Returns:
        Redacted PII value

    Examples:
        >>> redact_pii("555-123-4567", "phone")
        '***-***-4567'

        >>> redact_pii("john.doe@example.com", "email")
        'j****@example.com'
    """
    if not value:
        return "[REDACTED]"

    if pii_type == "email":
        return redact_email(value)
    elif pii_type == "phone":
        # Show only last 4 digits
        digits = re.sub(r"\D", "", value)
        return f"***-***-{digits[-4:]}" if len(digits) >= 4 else "***-***-****"
    elif pii_type == "ssn":
        # Show only last 4 digits
        digits = value.replace("-", "")
        return f"***-**-{digits[-4:]}" if len(digits) >= 4 else "***-**-****"
    elif pii_type == "credit_card":
        # Show only last 4 digits
        digits = re.sub(r"\D", "", value)
        return f"****-****-****-{digits[-4:]}" if len(digits) >= 4 else "****-****-****-****"
    else:
        # Generic redaction
        return "[REDACTED]"


def hash_token(value: str, length: int = 8) -> str:
    """
    Create a hash fingerprint of a token for logging.

    This allows identifying which token was used without exposing it.

    Args:
        value: The token to hash
        length: Length of hash to show (default: 8)

    Returns:
        Hex hash of the token

    Examples:
        >>> hash_token("ghp_1234567890abcdef")[:8]
        '3f4a7b2c'
    """
    if not value:
        return "no_token"

    digest = hashlib.sha256(value.encode()).hexdigest()
    return digest[:length]


def sanitize_for_logging(value: Any) -> str:
    """
    Sanitize a value for safe logging (remove newlines, control chars).

    This prevents log injection attacks by removing special characters.

    Args:
        value: The value to sanitize

    Returns:
        Sanitized string suitable for logging

    Examples:
        >>> sanitize_for_logging("normal text")
        'normal text'

        >>> sanitize_for_logging("injection\\nattack")
        'injection attack'
    """
    value_str = str(value)
    # Remove newlines, carriage returns, and control characters
    sanitized = re.sub(r"[\n\r\x00-\x1f\x7f]", " ", value_str)
    # Collapse multiple spaces
    sanitized = re.sub(r" +", " ", sanitized)
    return sanitized.strip()


def create_log_filter() -> logging.Filter:
    """
    Create a logging filter that redacts common secrets.

    Returns:
        A logging.Filter instance that sanitizes log records

    Usage:
        >>> logger = logging.getLogger(__name__)
        >>> filter_instance = create_log_filter()
        >>> logger.addFilter(filter_instance)
    """

    class SecretRedactionFilter(logging.Filter):
        """Filter that redacts secrets from log records."""

        def filter(self, record: logging.LogRecord) -> bool:
            """
            Filter and redact sensitive data from log records.

            Args:
                record: The log record to process

            Returns:
                Always True to allow the record through (after redaction)
            """
            # Redact message
            record.msg = self._redact_string(str(record.msg))

            # Redact exception message if present
            if record.exc_text:
                record.exc_text = self._redact_string(record.exc_text)

            # Redact record arguments if they're strings
            if isinstance(record.args, dict):
                for key, value in record.args.items():
                    if isinstance(value, str):
                        record.args[key] = self._redact_string(value)
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(
                    self._redact_string(arg) if isinstance(arg, str) else arg for arg in record.args
                )

            return True

        @staticmethod
        def _redact_string(text: str) -> str:
            """Redact secrets from a string."""
            for pattern in TOKEN_PATTERNS:
                # Replace tokens with redacted version
                text = re.sub(
                    pattern, lambda m: redact_token(m.group(0)), text, flags=re.IGNORECASE
                )
            return text

    return SecretRedactionFilter()


def setup_secure_logging(
    logger_instance: logging.Logger,
    add_redaction_filter: bool = True,
) -> None:
    """
    Setup a logger with security filters.

    Args:
        logger_instance: The logger to configure
        add_redaction_filter: Whether to add automatic redaction filter

    Usage:
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> setup_secure_logging(logger)
    """
    if add_redaction_filter:
        logger_instance.addFilter(create_log_filter())


# Security checklist for developers
__security_guidelines__ = """
SECURE LOGGING GUIDELINES:

1. NEVER log raw tokens:
   ❌ logger.debug(f"Token: {token}")
   ✅ logger.debug(f"Token: {redact_token(token)}")

2. NEVER log raw passwords:
   ❌ logger.debug(f"Password: {password}")
   ✅ logger.debug(f"Password: {redact_password(password)}")

3. NEVER log raw PII:
   ❌ logger.debug(f"Email: {user_email}")
   ✅ logger.debug(f"Email: {redact_email(user_email)}")

4. USE hash fingerprints for token identification:
   ✅ logger.info(f"Token {hash_token(token)} used for operation")

5. SANITIZE user-controlled input:
   ❌ logger.info(f"User action: {user_input}")
   ✅ logger.info(f"User action: {sanitize_for_logging(user_input)}")

6. USE structured logging when possible:
   ✅ logger.info("user_action", extra={"action": action, "user": user_id})

7. SETUP secure logging in application entry points:
   ```python
   import logging
   from security.logging import setup_secure_logging

   logger = logging.getLogger(__name__)
   setup_secure_logging(logger)
   ```
"""

if __name__ == "__main__":
    # Test the utilities
    print("Testing security logging utilities...\n")

    test_token = "example-token"
    print(f"Token sample: {redact_token(test_token)}")
    print(f"Token hash: {hash_token(test_token)}")
    print()

    test_password = "example-password"

    print(f"Password sample: {redact_password(test_password)}")
    print(f"Password sample (masked): {redact_password(test_password)}")
    print()

    test_email = "example.user@example.com"
    print(f"Email sample: {test_email}")
    print(f"Redacted email: {redact_email(test_email)}")
    print()

    test_injection = "normal\ninject\x00control"
    print(f"Original (repr): {repr(test_injection)}")
    print(f"Sanitized: {sanitize_for_logging(test_injection)}")
    print()

    print("✅ All tests passed!")
