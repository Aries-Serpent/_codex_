"""Security utilities consolidating validation, filtering, and secret handling.

Phase 3 Enhanced Security Hardening includes:
- Secure subprocess execution (B603)
- Secure exception handling (B110)
- Input validation (B311)
- Security event logging and audit trails
- API security (CORS, rate limiting, security headers)
- Cryptographic review and validation
- Comprehensive audit logging with PII protection
"""

from __future__ import annotations

from .api_security import (
    CORS_POLICY,
    RateLimiter,
    SecurityHeadersProvider,
    require_api_key,
    validate_request_signature,
    CORSPolicy,
)
from .audit_logging import (
    SecurityAuditLogger,
    SecurityEvent,
    SecurityEventSeverity,
    SecurityEventType,
    get_audit_logger,
    log_security_event,
)
from .content_filters import (
    detect_malware_patterns,
    detect_personal_data,
    detect_profanity,
    enforce_content_policies,
    sanitize_text,
)
from .core import (
    SecurityError,
    log_security_event as core_log_security_event,
    rate_limiter,
    sanitize_user_content,
    validate_input,
    verify_csrf_token,
    verify_session_integrity,
)
from .crypto_review import (
    CryptographicReviewer,
    CryptoStrength,
    DEFAULT_CRYPTO_CONFIG,
    TLSVersion,
    get_crypto_strength_assessment,
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
    # From core
    "CORS_POLICY",
    "CORSPolicy",
    "CryptographicReviewer",
    "CryptoStrength",
    "DEFAULT_CRYPTO_CONFIG",
    "EncryptionError",
    "InputValidationError",
    "RateLimiter",
    "SAFE_EXECUTABLES",
    "SecretRotationPolicy",
    "SecretRotationState",
    "SecurityAuditLogger",
    "SecurityError",
    "SecurityEvent",
    "SecurityEventSeverity",
    "SecurityEventType",
    "SecurityHeadersProvider",
    "SubprocessSecurityError",
    "TLSVersion",
    "check_secret_entropy",
    "core_log_security_event",
    "decrypt",
    "detect_malware_patterns",
    "detect_personal_data",
    "detect_profanity",
    "encrypt",
    "enforce_content_policies",
    "generate_key",
    "get_audit_logger",
    "get_crypto_strength_assessment",
    "get_secure_random_int",
    "is_security_critical",
    "log_security_event",
    "rate_limiter",
    "require_api_key",
    "rotate_secret",
    "sanitize_for_logging",
    "sanitize_text",
    "sanitize_user_content",
    "secure_exception_handler",
    "secure_subprocess_run",
    "validate_file_path",
    "validate_input",
    "validate_input_string",
    "validate_request_signature",
    "validate_subprocess_command",
    "verify_csrf_token",
    "verify_session_integrity",
]
