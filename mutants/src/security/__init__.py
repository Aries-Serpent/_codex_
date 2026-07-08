"""Security utilities consolidating validation, filtering, and secret handling."""

from __future__ import annotations

from .content_filters import (
    detect_malware_patterns,
    detect_personal_data,
    detect_profanity,
    enforce_content_policies,
    sanitize_text,
)
from .core import (
    SecurityError,
    log_security_event,
    rate_limiter,
    sanitize_user_content,
    validate_input,
    verify_csrf_token,
    verify_session_integrity,
)
from .encryption import EncryptionError, decrypt, encrypt, generate_key
from .secrets import (
    SecretRotationPolicy,
    SecretRotationState,
    check_secret_entropy,
    rotate_secret,
)

__all__ = [
    "EncryptionError",
    "SecretRotationPolicy",
    "SecretRotationState",
    "SecurityError",
    "check_secret_entropy",
    "decrypt",
    "detect_malware_patterns",
    "detect_personal_data",
    "detect_profanity",
    "encrypt",
    "enforce_content_policies",
    "generate_key",
    "log_security_event",
    "rate_limiter",
    "rotate_secret",
    "sanitize_text",
    "sanitize_user_content",
    "validate_input",
    "verify_csrf_token",
    "verify_session_integrity",
]
