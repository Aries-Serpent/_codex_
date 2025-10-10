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
from .secrets import SecretRotationPolicy, SecretRotationState, check_secret_entropy, rotate_secret

__all__ = [
    "SecurityError",
    "validate_input",
    "sanitize_user_content",
    "rate_limiter",
    "verify_csrf_token",
    "verify_session_integrity",
    "log_security_event",
    "check_secret_entropy",
    "rotate_secret",
    "SecretRotationPolicy",
    "SecretRotationState",
    "detect_profanity",
    "detect_personal_data",
    "detect_malware_patterns",
    "sanitize_text",
    "enforce_content_policies",
    "generate_key",
    "encrypt",
    "decrypt",
    "EncryptionError",
]
