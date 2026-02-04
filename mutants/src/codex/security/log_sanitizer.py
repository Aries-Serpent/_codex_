"""
Log sanitization utilities to prevent sensitive data exposure and log injection.

This module provides comprehensive sanitization for logging sensitive information
and preventing log injection attacks.

Security Features:
- Automatic redaction of sensitive patterns (API keys, tokens, passwords)
- Prevention of log injection via newline/control character removal
- Support for structured logging with extra fields
- Pattern-based detection and masking

Usage:
    from codex.security.log_sanitizer import sanitize_log, mask_sensitive
    
    # Sanitize user input
    logger.info(f"User {sanitize_log(username)} logged in")
    
    # Mask sensitive data
    safe_message = mask_sensitive(message_with_token)
    logger.info(safe_message)
"""

import re
from typing import Any, Pattern


# Patterns for detecting sensitive data
SENSITIVE_PATTERNS: list[tuple[Pattern[str], str]] = [
    # API keys and tokens
    (re.compile(r'(api[_-]?key|token|secret|password)\s*[=:]\s*["\']?(\S+)', re.IGNORECASE), 
     r'\1=***REDACTED***'),
    
    # Bearer tokens
    (re.compile(r'Bearer\s+\S+', re.IGNORECASE), 
     'Bearer ***REDACTED***'),
    
    # Base64-encoded secrets (40+ chars)
    (re.compile(r'[a-zA-Z0-9+/]{40,}={0,2}'), 
     '***BASE64_REDACTED***'),
    
    # Hex-encoded secrets (32+ chars)
    (re.compile(r'\b[a-fA-F0-9]{32,}\b'), 
     '***HEX_REDACTED***'),
    
    # AWS keys
    (re.compile(r'AKIA[0-9A-Z]{16}'), 
     '***AWS_KEY_REDACTED***'),
    
    # JWT tokens
    (re.compile(r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'), 
     '***JWT_REDACTED***'),
    
    # Private keys
    (re.compile(r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----.*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----', 
                re.DOTALL), 
     '***PRIVATE_KEY_REDACTED***'),
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


def x_sanitize_log__mutmut_orig(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_1(value: Any, max_length: int = 501) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_2(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is not None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_3(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "XXNoneXX"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_4(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "none"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_5(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "NONE"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_6(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = None
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_7(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(None)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_8(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = None
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_9(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(None, '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_10(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', None, str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_11(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', None)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_12(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub('', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_13(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_14(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', )
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_15(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'XX[\n\r\t\x00-\x1f\x7f-\x9f]XX', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_16(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1F\x7F-\x9F]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_17(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', 'XXXX', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_18(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = None
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_19(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(None, '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_20(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', None, sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_21(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', None)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_22(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub('', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_23(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_24(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', )
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_25(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'XX\x1b\[[0-9;]*mXX', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_26(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1B\[[0-9;]*M', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_27(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', 'XXXX', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_28(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) >= max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_29(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = None
    
    return sanitized


def x_sanitize_log__mutmut_30(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] - '...[truncated]'
    
    return sanitized


def x_sanitize_log__mutmut_31(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + 'XX...[truncated]XX'
    
    return sanitized


def x_sanitize_log__mutmut_32(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.
    
    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str_value)
    
    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[TRUNCATED]'
    
    return sanitized

x_sanitize_log__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_log__mutmut_1': x_sanitize_log__mutmut_1, 
    'x_sanitize_log__mutmut_2': x_sanitize_log__mutmut_2, 
    'x_sanitize_log__mutmut_3': x_sanitize_log__mutmut_3, 
    'x_sanitize_log__mutmut_4': x_sanitize_log__mutmut_4, 
    'x_sanitize_log__mutmut_5': x_sanitize_log__mutmut_5, 
    'x_sanitize_log__mutmut_6': x_sanitize_log__mutmut_6, 
    'x_sanitize_log__mutmut_7': x_sanitize_log__mutmut_7, 
    'x_sanitize_log__mutmut_8': x_sanitize_log__mutmut_8, 
    'x_sanitize_log__mutmut_9': x_sanitize_log__mutmut_9, 
    'x_sanitize_log__mutmut_10': x_sanitize_log__mutmut_10, 
    'x_sanitize_log__mutmut_11': x_sanitize_log__mutmut_11, 
    'x_sanitize_log__mutmut_12': x_sanitize_log__mutmut_12, 
    'x_sanitize_log__mutmut_13': x_sanitize_log__mutmut_13, 
    'x_sanitize_log__mutmut_14': x_sanitize_log__mutmut_14, 
    'x_sanitize_log__mutmut_15': x_sanitize_log__mutmut_15, 
    'x_sanitize_log__mutmut_16': x_sanitize_log__mutmut_16, 
    'x_sanitize_log__mutmut_17': x_sanitize_log__mutmut_17, 
    'x_sanitize_log__mutmut_18': x_sanitize_log__mutmut_18, 
    'x_sanitize_log__mutmut_19': x_sanitize_log__mutmut_19, 
    'x_sanitize_log__mutmut_20': x_sanitize_log__mutmut_20, 
    'x_sanitize_log__mutmut_21': x_sanitize_log__mutmut_21, 
    'x_sanitize_log__mutmut_22': x_sanitize_log__mutmut_22, 
    'x_sanitize_log__mutmut_23': x_sanitize_log__mutmut_23, 
    'x_sanitize_log__mutmut_24': x_sanitize_log__mutmut_24, 
    'x_sanitize_log__mutmut_25': x_sanitize_log__mutmut_25, 
    'x_sanitize_log__mutmut_26': x_sanitize_log__mutmut_26, 
    'x_sanitize_log__mutmut_27': x_sanitize_log__mutmut_27, 
    'x_sanitize_log__mutmut_28': x_sanitize_log__mutmut_28, 
    'x_sanitize_log__mutmut_29': x_sanitize_log__mutmut_29, 
    'x_sanitize_log__mutmut_30': x_sanitize_log__mutmut_30, 
    'x_sanitize_log__mutmut_31': x_sanitize_log__mutmut_31, 
    'x_sanitize_log__mutmut_32': x_sanitize_log__mutmut_32
}

def sanitize_log(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_log__mutmut_orig, x_sanitize_log__mutmut_mutants, args, kwargs)
    return result 

sanitize_log.__signature__ = _mutmut_signature(x_sanitize_log__mutmut_orig)
x_sanitize_log__mutmut_orig.__name__ = 'x_sanitize_log'


def x_mask_sensitive__mutmut_orig(message: str) -> str:
    """
    Mask sensitive data patterns in a message.
    
    Automatically detects and redacts common sensitive patterns like:
    - API keys and tokens
    - Bearer tokens
    - Base64/hex-encoded secrets
    - AWS credentials
    - JWT tokens
    - Private keys
    
    Args:
        message: Message that may contain sensitive data
        
    Returns:
        Message with sensitive patterns redacted
        
    Example:
        >>> mask_sensitive("Token: sk_live_abc123xyz789")
        'Token: ***REDACTED***'
        >>> mask_sensitive("Bearer eyJhbGc...")
        'Bearer ***JWT_REDACTED***'
    """
    masked = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked


def x_mask_sensitive__mutmut_1(message: str) -> str:
    """
    Mask sensitive data patterns in a message.
    
    Automatically detects and redacts common sensitive patterns like:
    - API keys and tokens
    - Bearer tokens
    - Base64/hex-encoded secrets
    - AWS credentials
    - JWT tokens
    - Private keys
    
    Args:
        message: Message that may contain sensitive data
        
    Returns:
        Message with sensitive patterns redacted
        
    Example:
        >>> mask_sensitive("Token: sk_live_abc123xyz789")
        'Token: ***REDACTED***'
        >>> mask_sensitive("Bearer eyJhbGc...")
        'Bearer ***JWT_REDACTED***'
    """
    masked = None
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked


def x_mask_sensitive__mutmut_2(message: str) -> str:
    """
    Mask sensitive data patterns in a message.
    
    Automatically detects and redacts common sensitive patterns like:
    - API keys and tokens
    - Bearer tokens
    - Base64/hex-encoded secrets
    - AWS credentials
    - JWT tokens
    - Private keys
    
    Args:
        message: Message that may contain sensitive data
        
    Returns:
        Message with sensitive patterns redacted
        
    Example:
        >>> mask_sensitive("Token: sk_live_abc123xyz789")
        'Token: ***REDACTED***'
        >>> mask_sensitive("Bearer eyJhbGc...")
        'Bearer ***JWT_REDACTED***'
    """
    masked = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = None
    return masked


def x_mask_sensitive__mutmut_3(message: str) -> str:
    """
    Mask sensitive data patterns in a message.
    
    Automatically detects and redacts common sensitive patterns like:
    - API keys and tokens
    - Bearer tokens
    - Base64/hex-encoded secrets
    - AWS credentials
    - JWT tokens
    - Private keys
    
    Args:
        message: Message that may contain sensitive data
        
    Returns:
        Message with sensitive patterns redacted
        
    Example:
        >>> mask_sensitive("Token: sk_live_abc123xyz789")
        'Token: ***REDACTED***'
        >>> mask_sensitive("Bearer eyJhbGc...")
        'Bearer ***JWT_REDACTED***'
    """
    masked = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = pattern.sub(None, masked)
    return masked


def x_mask_sensitive__mutmut_4(message: str) -> str:
    """
    Mask sensitive data patterns in a message.
    
    Automatically detects and redacts common sensitive patterns like:
    - API keys and tokens
    - Bearer tokens
    - Base64/hex-encoded secrets
    - AWS credentials
    - JWT tokens
    - Private keys
    
    Args:
        message: Message that may contain sensitive data
        
    Returns:
        Message with sensitive patterns redacted
        
    Example:
        >>> mask_sensitive("Token: sk_live_abc123xyz789")
        'Token: ***REDACTED***'
        >>> mask_sensitive("Bearer eyJhbGc...")
        'Bearer ***JWT_REDACTED***'
    """
    masked = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = pattern.sub(replacement, None)
    return masked


def x_mask_sensitive__mutmut_5(message: str) -> str:
    """
    Mask sensitive data patterns in a message.
    
    Automatically detects and redacts common sensitive patterns like:
    - API keys and tokens
    - Bearer tokens
    - Base64/hex-encoded secrets
    - AWS credentials
    - JWT tokens
    - Private keys
    
    Args:
        message: Message that may contain sensitive data
        
    Returns:
        Message with sensitive patterns redacted
        
    Example:
        >>> mask_sensitive("Token: sk_live_abc123xyz789")
        'Token: ***REDACTED***'
        >>> mask_sensitive("Bearer eyJhbGc...")
        'Bearer ***JWT_REDACTED***'
    """
    masked = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = pattern.sub(masked)
    return masked


def x_mask_sensitive__mutmut_6(message: str) -> str:
    """
    Mask sensitive data patterns in a message.
    
    Automatically detects and redacts common sensitive patterns like:
    - API keys and tokens
    - Bearer tokens
    - Base64/hex-encoded secrets
    - AWS credentials
    - JWT tokens
    - Private keys
    
    Args:
        message: Message that may contain sensitive data
        
    Returns:
        Message with sensitive patterns redacted
        
    Example:
        >>> mask_sensitive("Token: sk_live_abc123xyz789")
        'Token: ***REDACTED***'
        >>> mask_sensitive("Bearer eyJhbGc...")
        'Bearer ***JWT_REDACTED***'
    """
    masked = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = pattern.sub(replacement, )
    return masked

x_mask_sensitive__mutmut_mutants : ClassVar[MutantDict] = {
'x_mask_sensitive__mutmut_1': x_mask_sensitive__mutmut_1, 
    'x_mask_sensitive__mutmut_2': x_mask_sensitive__mutmut_2, 
    'x_mask_sensitive__mutmut_3': x_mask_sensitive__mutmut_3, 
    'x_mask_sensitive__mutmut_4': x_mask_sensitive__mutmut_4, 
    'x_mask_sensitive__mutmut_5': x_mask_sensitive__mutmut_5, 
    'x_mask_sensitive__mutmut_6': x_mask_sensitive__mutmut_6
}

def mask_sensitive(*args, **kwargs):
    result = _mutmut_trampoline(x_mask_sensitive__mutmut_orig, x_mask_sensitive__mutmut_mutants, args, kwargs)
    return result 

mask_sensitive.__signature__ = _mutmut_signature(x_mask_sensitive__mutmut_orig)
x_mask_sensitive__mutmut_orig.__name__ = 'x_mask_sensitive'


def x_safe_log_message__mutmut_orig(message: str, mask_secrets: bool = True) -> str:
    """
    Comprehensive log message sanitization.
    
    Combines both control character removal and sensitive data masking
    for maximum security.
    
    Args:
        message: Message to sanitize
        mask_secrets: Whether to mask sensitive patterns (default: True)
        
    Returns:
        Fully sanitized and masked message
        
    Example:
        >>> safe_log_message("User api_key=sk_test_123\\nFAKE_LOG logged in")
        'User api_key=***REDACTED*** FAKE_LOG logged in'
    """
    # First remove control characters
    sanitized = sanitize_log(message)
    
    # Then mask sensitive patterns if requested
    if mask_secrets:
        sanitized = mask_sensitive(sanitized)
    
    return sanitized


def x_safe_log_message__mutmut_1(message: str, mask_secrets: bool = False) -> str:
    """
    Comprehensive log message sanitization.
    
    Combines both control character removal and sensitive data masking
    for maximum security.
    
    Args:
        message: Message to sanitize
        mask_secrets: Whether to mask sensitive patterns (default: True)
        
    Returns:
        Fully sanitized and masked message
        
    Example:
        >>> safe_log_message("User api_key=sk_test_123\\nFAKE_LOG logged in")
        'User api_key=***REDACTED*** FAKE_LOG logged in'
    """
    # First remove control characters
    sanitized = sanitize_log(message)
    
    # Then mask sensitive patterns if requested
    if mask_secrets:
        sanitized = mask_sensitive(sanitized)
    
    return sanitized


def x_safe_log_message__mutmut_2(message: str, mask_secrets: bool = True) -> str:
    """
    Comprehensive log message sanitization.
    
    Combines both control character removal and sensitive data masking
    for maximum security.
    
    Args:
        message: Message to sanitize
        mask_secrets: Whether to mask sensitive patterns (default: True)
        
    Returns:
        Fully sanitized and masked message
        
    Example:
        >>> safe_log_message("User api_key=sk_test_123\\nFAKE_LOG logged in")
        'User api_key=***REDACTED*** FAKE_LOG logged in'
    """
    # First remove control characters
    sanitized = None
    
    # Then mask sensitive patterns if requested
    if mask_secrets:
        sanitized = mask_sensitive(sanitized)
    
    return sanitized


def x_safe_log_message__mutmut_3(message: str, mask_secrets: bool = True) -> str:
    """
    Comprehensive log message sanitization.
    
    Combines both control character removal and sensitive data masking
    for maximum security.
    
    Args:
        message: Message to sanitize
        mask_secrets: Whether to mask sensitive patterns (default: True)
        
    Returns:
        Fully sanitized and masked message
        
    Example:
        >>> safe_log_message("User api_key=sk_test_123\\nFAKE_LOG logged in")
        'User api_key=***REDACTED*** FAKE_LOG logged in'
    """
    # First remove control characters
    sanitized = sanitize_log(None)
    
    # Then mask sensitive patterns if requested
    if mask_secrets:
        sanitized = mask_sensitive(sanitized)
    
    return sanitized


def x_safe_log_message__mutmut_4(message: str, mask_secrets: bool = True) -> str:
    """
    Comprehensive log message sanitization.
    
    Combines both control character removal and sensitive data masking
    for maximum security.
    
    Args:
        message: Message to sanitize
        mask_secrets: Whether to mask sensitive patterns (default: True)
        
    Returns:
        Fully sanitized and masked message
        
    Example:
        >>> safe_log_message("User api_key=sk_test_123\\nFAKE_LOG logged in")
        'User api_key=***REDACTED*** FAKE_LOG logged in'
    """
    # First remove control characters
    sanitized = sanitize_log(message)
    
    # Then mask sensitive patterns if requested
    if mask_secrets:
        sanitized = None
    
    return sanitized


def x_safe_log_message__mutmut_5(message: str, mask_secrets: bool = True) -> str:
    """
    Comprehensive log message sanitization.
    
    Combines both control character removal and sensitive data masking
    for maximum security.
    
    Args:
        message: Message to sanitize
        mask_secrets: Whether to mask sensitive patterns (default: True)
        
    Returns:
        Fully sanitized and masked message
        
    Example:
        >>> safe_log_message("User api_key=sk_test_123\\nFAKE_LOG logged in")
        'User api_key=***REDACTED*** FAKE_LOG logged in'
    """
    # First remove control characters
    sanitized = sanitize_log(message)
    
    # Then mask sensitive patterns if requested
    if mask_secrets:
        sanitized = mask_sensitive(None)
    
    return sanitized

x_safe_log_message__mutmut_mutants : ClassVar[MutantDict] = {
'x_safe_log_message__mutmut_1': x_safe_log_message__mutmut_1, 
    'x_safe_log_message__mutmut_2': x_safe_log_message__mutmut_2, 
    'x_safe_log_message__mutmut_3': x_safe_log_message__mutmut_3, 
    'x_safe_log_message__mutmut_4': x_safe_log_message__mutmut_4, 
    'x_safe_log_message__mutmut_5': x_safe_log_message__mutmut_5
}

def safe_log_message(*args, **kwargs):
    result = _mutmut_trampoline(x_safe_log_message__mutmut_orig, x_safe_log_message__mutmut_mutants, args, kwargs)
    return result 

safe_log_message.__signature__ = _mutmut_signature(x_safe_log_message__mutmut_orig)
x_safe_log_message__mutmut_orig.__name__ = 'x_safe_log_message'


def x_sanitize_dict_for_log__mutmut_orig(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_1(data: dict, max_length: int = 501, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_2(data: dict, max_length: int = 500, mask_secrets: bool = False) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_3(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = None
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_4(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = None
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_5(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(None, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_6(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, None, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_7(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, None)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_8(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_9(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_10(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, )
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_11(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = None
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_12(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(None) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_13(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(None, max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_14(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), None)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_15(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_16(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), )) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_17(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(None), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_18(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_19(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(None, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_20(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, None, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_21(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, None)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_22(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_23(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_24(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, )
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_25(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = None
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_26(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(None, max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_27(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), None) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_28(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_29(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), ) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_30(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(None), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_31(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_32(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(None, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_33(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, None, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_34(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, None)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_35(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_36(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_37(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, )
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_38(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = None
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_39(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(None, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_40(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, None)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_41(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_42(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, )
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_43(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = None
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_44(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(None)
            result[key] = str_value
    return result


def x_sanitize_dict_for_log__mutmut_45(data: dict, max_length: int = 500, mask_secrets: bool = True) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [
                    mask_sensitive(sanitize_log(str(item), max_length)) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
            else:
                result[key] = [
                    sanitize_log(str(item), max_length) if not isinstance(item, dict)
                    else sanitize_dict_for_log(item, max_length, mask_secrets)
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = None
    return result

x_sanitize_dict_for_log__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_dict_for_log__mutmut_1': x_sanitize_dict_for_log__mutmut_1, 
    'x_sanitize_dict_for_log__mutmut_2': x_sanitize_dict_for_log__mutmut_2, 
    'x_sanitize_dict_for_log__mutmut_3': x_sanitize_dict_for_log__mutmut_3, 
    'x_sanitize_dict_for_log__mutmut_4': x_sanitize_dict_for_log__mutmut_4, 
    'x_sanitize_dict_for_log__mutmut_5': x_sanitize_dict_for_log__mutmut_5, 
    'x_sanitize_dict_for_log__mutmut_6': x_sanitize_dict_for_log__mutmut_6, 
    'x_sanitize_dict_for_log__mutmut_7': x_sanitize_dict_for_log__mutmut_7, 
    'x_sanitize_dict_for_log__mutmut_8': x_sanitize_dict_for_log__mutmut_8, 
    'x_sanitize_dict_for_log__mutmut_9': x_sanitize_dict_for_log__mutmut_9, 
    'x_sanitize_dict_for_log__mutmut_10': x_sanitize_dict_for_log__mutmut_10, 
    'x_sanitize_dict_for_log__mutmut_11': x_sanitize_dict_for_log__mutmut_11, 
    'x_sanitize_dict_for_log__mutmut_12': x_sanitize_dict_for_log__mutmut_12, 
    'x_sanitize_dict_for_log__mutmut_13': x_sanitize_dict_for_log__mutmut_13, 
    'x_sanitize_dict_for_log__mutmut_14': x_sanitize_dict_for_log__mutmut_14, 
    'x_sanitize_dict_for_log__mutmut_15': x_sanitize_dict_for_log__mutmut_15, 
    'x_sanitize_dict_for_log__mutmut_16': x_sanitize_dict_for_log__mutmut_16, 
    'x_sanitize_dict_for_log__mutmut_17': x_sanitize_dict_for_log__mutmut_17, 
    'x_sanitize_dict_for_log__mutmut_18': x_sanitize_dict_for_log__mutmut_18, 
    'x_sanitize_dict_for_log__mutmut_19': x_sanitize_dict_for_log__mutmut_19, 
    'x_sanitize_dict_for_log__mutmut_20': x_sanitize_dict_for_log__mutmut_20, 
    'x_sanitize_dict_for_log__mutmut_21': x_sanitize_dict_for_log__mutmut_21, 
    'x_sanitize_dict_for_log__mutmut_22': x_sanitize_dict_for_log__mutmut_22, 
    'x_sanitize_dict_for_log__mutmut_23': x_sanitize_dict_for_log__mutmut_23, 
    'x_sanitize_dict_for_log__mutmut_24': x_sanitize_dict_for_log__mutmut_24, 
    'x_sanitize_dict_for_log__mutmut_25': x_sanitize_dict_for_log__mutmut_25, 
    'x_sanitize_dict_for_log__mutmut_26': x_sanitize_dict_for_log__mutmut_26, 
    'x_sanitize_dict_for_log__mutmut_27': x_sanitize_dict_for_log__mutmut_27, 
    'x_sanitize_dict_for_log__mutmut_28': x_sanitize_dict_for_log__mutmut_28, 
    'x_sanitize_dict_for_log__mutmut_29': x_sanitize_dict_for_log__mutmut_29, 
    'x_sanitize_dict_for_log__mutmut_30': x_sanitize_dict_for_log__mutmut_30, 
    'x_sanitize_dict_for_log__mutmut_31': x_sanitize_dict_for_log__mutmut_31, 
    'x_sanitize_dict_for_log__mutmut_32': x_sanitize_dict_for_log__mutmut_32, 
    'x_sanitize_dict_for_log__mutmut_33': x_sanitize_dict_for_log__mutmut_33, 
    'x_sanitize_dict_for_log__mutmut_34': x_sanitize_dict_for_log__mutmut_34, 
    'x_sanitize_dict_for_log__mutmut_35': x_sanitize_dict_for_log__mutmut_35, 
    'x_sanitize_dict_for_log__mutmut_36': x_sanitize_dict_for_log__mutmut_36, 
    'x_sanitize_dict_for_log__mutmut_37': x_sanitize_dict_for_log__mutmut_37, 
    'x_sanitize_dict_for_log__mutmut_38': x_sanitize_dict_for_log__mutmut_38, 
    'x_sanitize_dict_for_log__mutmut_39': x_sanitize_dict_for_log__mutmut_39, 
    'x_sanitize_dict_for_log__mutmut_40': x_sanitize_dict_for_log__mutmut_40, 
    'x_sanitize_dict_for_log__mutmut_41': x_sanitize_dict_for_log__mutmut_41, 
    'x_sanitize_dict_for_log__mutmut_42': x_sanitize_dict_for_log__mutmut_42, 
    'x_sanitize_dict_for_log__mutmut_43': x_sanitize_dict_for_log__mutmut_43, 
    'x_sanitize_dict_for_log__mutmut_44': x_sanitize_dict_for_log__mutmut_44, 
    'x_sanitize_dict_for_log__mutmut_45': x_sanitize_dict_for_log__mutmut_45
}

def sanitize_dict_for_log(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_dict_for_log__mutmut_orig, x_sanitize_dict_for_log__mutmut_mutants, args, kwargs)
    return result 

sanitize_dict_for_log.__signature__ = _mutmut_signature(x_sanitize_dict_for_log__mutmut_orig)
x_sanitize_dict_for_log__mutmut_orig.__name__ = 'x_sanitize_dict_for_log'


# Shorthand aliases
safe_log = sanitize_log
mask_secrets = mask_sensitive


__all__ = [
    'sanitize_log',
    'mask_sensitive',
    'safe_log_message',
    'sanitize_dict_for_log',
    'safe_log',
    'mask_secrets',
]
