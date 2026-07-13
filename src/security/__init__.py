"""Security utilities consolidating validation, filtering, and secret handling.

Phase 3 Enhanced Security Hardening includes:
- Secure subprocess execution (B603)
- Secure exception handling (B110)
- Input validation (B311)
- Security event logging and audit trails
"""

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
from .security_hardening import (
    SAFE_EXECUTABLES,
    InputValidationError,
    SubprocessSecurityError,
    get_secure_random_int,
    is_security_critical,
    sanitize_for_logging,
    secure_exception_handler,
    secure_subprocess_run,
    validate_file_path,
    validate_input_string,
    validate_subprocess_command,
)

__all__ = [
    "EncryptionError",
    "InputValidationError",
    "SAFE_EXECUTABLES",
    "SecretRotationPolicy",
    "SecretRotationState",
    "SecurityError",
    "SubprocessSecurityError",
    "check_secret_entropy",
    "decrypt",
    "detect_malware_patterns",
    "detect_personal_data",
    "detect_profanity",
    "encrypt",
    "enforce_content_policies",
    "generate_key",
    "get_secure_random_int",
    "is_security_critical",
    "log_security_event",
    "rate_limiter",
    "rotate_secret",
    "sanitize_for_logging",
    "sanitize_text",
    "sanitize_user_content",
    "secure_exception_handler",
    "secure_subprocess_run",
    "validate_file_path",
    "validate_input",
    "validate_input_string",
    "validate_subprocess_command",
    "verify_csrf_token",
    "verify_session_integrity",
]
