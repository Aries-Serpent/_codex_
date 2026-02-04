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
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result
