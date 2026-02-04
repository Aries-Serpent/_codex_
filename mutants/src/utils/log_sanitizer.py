"""
Log sanitization utilities to prevent log injection attacks.

This module provides functions to sanitize user-controlled input before
including it in log statements, preventing log forging and injection attacks.

Security Rationale:
-------------------
User-controlled data in logs can allow attackers to:
- Inject fake log entries by including newline characters
- Hide malicious activity by injecting ANSI escape codes
- Corrupt log parsers with control characters

Always use sanitize_log_input() for any user-provided data in logs.

Example:
    >>> from src.utils.log_sanitizer import sanitize_log_input
    >>> logger.info(f"User {sanitize_log_input(user_input)} logged in")
"""

import re
from typing import Any
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


def x_sanitize_log_input__mutmut_orig(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_1(value: Any, max_length: int = 501) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_2(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is not None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_3(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "XXNoneXX"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_4(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "none"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_5(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "NONE"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_6(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = None
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_7(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(None)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_8(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = None
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_9(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(None, '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_10(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', None, str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_11(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', None)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_12(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub('', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_13(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_14(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', )
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_15(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'XX\x1b\[[0-9;]*mXX', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_16(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1B\[[0-9;]*M', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_17(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', 'XXXX', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_18(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = None

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_19(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(None, '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_20(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', None, sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_21(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', None)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_22(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub('', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_23(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_24(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', )

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_25(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'XX\[[0-9;]*mXX', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_26(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*M', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_27(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', 'XXXX', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_28(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = None
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_29(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(None, '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_30(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', None, sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_31(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', None)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_32(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub('', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_33(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_34(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', )
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_35(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'XX[\n\r\t\x00-\x1f\x7f-\x9f]XX', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_36(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1F\x7F-\x9F]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_37(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', 'XXXX', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_38(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) >= max_length:
        sanitized = sanitized[:max_length] + '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_39(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = None
    
    return sanitized


def x_sanitize_log_input__mutmut_40(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] - '...[truncated]'
    
    return sanitized


def x_sanitize_log_input__mutmut_41(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + 'XX...[truncated]XX'
    
    return sanitized


def x_sanitize_log_input__mutmut_42(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.
    
    Removes control characters and truncates to prevent log injection attacks.
    
    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes
    
    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', str_value)
    sanitized = re.sub(r'\[[0-9;]*m', '', sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[TRUNCATED]'
    
    return sanitized

x_sanitize_log_input__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_log_input__mutmut_1': x_sanitize_log_input__mutmut_1, 
    'x_sanitize_log_input__mutmut_2': x_sanitize_log_input__mutmut_2, 
    'x_sanitize_log_input__mutmut_3': x_sanitize_log_input__mutmut_3, 
    'x_sanitize_log_input__mutmut_4': x_sanitize_log_input__mutmut_4, 
    'x_sanitize_log_input__mutmut_5': x_sanitize_log_input__mutmut_5, 
    'x_sanitize_log_input__mutmut_6': x_sanitize_log_input__mutmut_6, 
    'x_sanitize_log_input__mutmut_7': x_sanitize_log_input__mutmut_7, 
    'x_sanitize_log_input__mutmut_8': x_sanitize_log_input__mutmut_8, 
    'x_sanitize_log_input__mutmut_9': x_sanitize_log_input__mutmut_9, 
    'x_sanitize_log_input__mutmut_10': x_sanitize_log_input__mutmut_10, 
    'x_sanitize_log_input__mutmut_11': x_sanitize_log_input__mutmut_11, 
    'x_sanitize_log_input__mutmut_12': x_sanitize_log_input__mutmut_12, 
    'x_sanitize_log_input__mutmut_13': x_sanitize_log_input__mutmut_13, 
    'x_sanitize_log_input__mutmut_14': x_sanitize_log_input__mutmut_14, 
    'x_sanitize_log_input__mutmut_15': x_sanitize_log_input__mutmut_15, 
    'x_sanitize_log_input__mutmut_16': x_sanitize_log_input__mutmut_16, 
    'x_sanitize_log_input__mutmut_17': x_sanitize_log_input__mutmut_17, 
    'x_sanitize_log_input__mutmut_18': x_sanitize_log_input__mutmut_18, 
    'x_sanitize_log_input__mutmut_19': x_sanitize_log_input__mutmut_19, 
    'x_sanitize_log_input__mutmut_20': x_sanitize_log_input__mutmut_20, 
    'x_sanitize_log_input__mutmut_21': x_sanitize_log_input__mutmut_21, 
    'x_sanitize_log_input__mutmut_22': x_sanitize_log_input__mutmut_22, 
    'x_sanitize_log_input__mutmut_23': x_sanitize_log_input__mutmut_23, 
    'x_sanitize_log_input__mutmut_24': x_sanitize_log_input__mutmut_24, 
    'x_sanitize_log_input__mutmut_25': x_sanitize_log_input__mutmut_25, 
    'x_sanitize_log_input__mutmut_26': x_sanitize_log_input__mutmut_26, 
    'x_sanitize_log_input__mutmut_27': x_sanitize_log_input__mutmut_27, 
    'x_sanitize_log_input__mutmut_28': x_sanitize_log_input__mutmut_28, 
    'x_sanitize_log_input__mutmut_29': x_sanitize_log_input__mutmut_29, 
    'x_sanitize_log_input__mutmut_30': x_sanitize_log_input__mutmut_30, 
    'x_sanitize_log_input__mutmut_31': x_sanitize_log_input__mutmut_31, 
    'x_sanitize_log_input__mutmut_32': x_sanitize_log_input__mutmut_32, 
    'x_sanitize_log_input__mutmut_33': x_sanitize_log_input__mutmut_33, 
    'x_sanitize_log_input__mutmut_34': x_sanitize_log_input__mutmut_34, 
    'x_sanitize_log_input__mutmut_35': x_sanitize_log_input__mutmut_35, 
    'x_sanitize_log_input__mutmut_36': x_sanitize_log_input__mutmut_36, 
    'x_sanitize_log_input__mutmut_37': x_sanitize_log_input__mutmut_37, 
    'x_sanitize_log_input__mutmut_38': x_sanitize_log_input__mutmut_38, 
    'x_sanitize_log_input__mutmut_39': x_sanitize_log_input__mutmut_39, 
    'x_sanitize_log_input__mutmut_40': x_sanitize_log_input__mutmut_40, 
    'x_sanitize_log_input__mutmut_41': x_sanitize_log_input__mutmut_41, 
    'x_sanitize_log_input__mutmut_42': x_sanitize_log_input__mutmut_42
}

def sanitize_log_input(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_log_input__mutmut_orig, x_sanitize_log_input__mutmut_mutants, args, kwargs)
    return result 

sanitize_log_input.__signature__ = _mutmut_signature(x_sanitize_log_input__mutmut_orig)
x_sanitize_log_input__mutmut_orig.__name__ = 'x_sanitize_log_input'


def x_sanitize_dict_for_log__mutmut_orig(data: dict, max_length: int = 500) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "id": 123})
        {'user': 'testinjection', 'id': '123'}
    """
    return {
        key: sanitize_log_input(value, max_length)
        for key, value in data.items()
    }


def x_sanitize_dict_for_log__mutmut_1(data: dict, max_length: int = 501) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "id": 123})
        {'user': 'testinjection', 'id': '123'}
    """
    return {
        key: sanitize_log_input(value, max_length)
        for key, value in data.items()
    }


def x_sanitize_dict_for_log__mutmut_2(data: dict, max_length: int = 500) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "id": 123})
        {'user': 'testinjection', 'id': '123'}
    """
    return {
        key: sanitize_log_input(None, max_length)
        for key, value in data.items()
    }


def x_sanitize_dict_for_log__mutmut_3(data: dict, max_length: int = 500) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "id": 123})
        {'user': 'testinjection', 'id': '123'}
    """
    return {
        key: sanitize_log_input(value, None)
        for key, value in data.items()
    }


def x_sanitize_dict_for_log__mutmut_4(data: dict, max_length: int = 500) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "id": 123})
        {'user': 'testinjection', 'id': '123'}
    """
    return {
        key: sanitize_log_input(max_length)
        for key, value in data.items()
    }


def x_sanitize_dict_for_log__mutmut_5(data: dict, max_length: int = 500) -> dict:
    """
    Sanitize all values in a dictionary for logging.
    
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled data.
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        
    Returns:
        New dictionary with sanitized values
        
    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "id": 123})
        {'user': 'testinjection', 'id': '123'}
    """
    return {
        key: sanitize_log_input(value, )
        for key, value in data.items()
    }

x_sanitize_dict_for_log__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_dict_for_log__mutmut_1': x_sanitize_dict_for_log__mutmut_1, 
    'x_sanitize_dict_for_log__mutmut_2': x_sanitize_dict_for_log__mutmut_2, 
    'x_sanitize_dict_for_log__mutmut_3': x_sanitize_dict_for_log__mutmut_3, 
    'x_sanitize_dict_for_log__mutmut_4': x_sanitize_dict_for_log__mutmut_4, 
    'x_sanitize_dict_for_log__mutmut_5': x_sanitize_dict_for_log__mutmut_5
}

def sanitize_dict_for_log(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_dict_for_log__mutmut_orig, x_sanitize_dict_for_log__mutmut_mutants, args, kwargs)
    return result 

sanitize_dict_for_log.__signature__ = _mutmut_signature(x_sanitize_dict_for_log__mutmut_orig)
x_sanitize_dict_for_log__mutmut_orig.__name__ = 'x_sanitize_dict_for_log'


# Shorthand alias for convenience
safe_log = sanitize_log_input

# Export alias for backward compatibility
sanitize_log = sanitize_log_input

# Ensure it's in __all__ if defined
__all__ = ['sanitize_log_input', 'safe_log', 'sanitize_log', 'sanitize_dict_for_log']
