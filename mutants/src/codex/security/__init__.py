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
from urllib.parse import urlparse

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


def x_sanitize_log__mutmut_1(value: Any, max_length: int = 501) -> str:
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


def x_sanitize_log__mutmut_2(value: Any, max_length: int = 500) -> str:
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
    return sanitize_log_input(None, max_length)


def x_sanitize_log__mutmut_3(value: Any, max_length: int = 500) -> str:
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
    return sanitize_log_input(value, None)


def x_sanitize_log__mutmut_4(value: Any, max_length: int = 500) -> str:
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
    return sanitize_log_input(max_length)


def x_sanitize_log__mutmut_5(value: Any, max_length: int = 500) -> str:
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
    return sanitize_log_input(value, )

x_sanitize_log__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_log__mutmut_1': x_sanitize_log__mutmut_1, 
    'x_sanitize_log__mutmut_2': x_sanitize_log__mutmut_2, 
    'x_sanitize_log__mutmut_3': x_sanitize_log__mutmut_3, 
    'x_sanitize_log__mutmut_4': x_sanitize_log__mutmut_4, 
    'x_sanitize_log__mutmut_5': x_sanitize_log__mutmut_5
}

def sanitize_log(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_log__mutmut_orig, x_sanitize_log__mutmut_mutants, args, kwargs)
    return result 

sanitize_log.__signature__ = _mutmut_signature(x_sanitize_log__mutmut_orig)
x_sanitize_log__mutmut_orig.__name__ = 'x_sanitize_log'


def x_hash_secure__mutmut_orig(data: str, algorithm: str = 'sha256') -> str:
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


def x_hash_secure__mutmut_1(data: str, algorithm: str = 'XXsha256XX') -> str:
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


def x_hash_secure__mutmut_2(data: str, algorithm: str = 'SHA256') -> str:
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


def x_hash_secure__mutmut_3(data: str, algorithm: str = 'sha256') -> str:
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
    if algorithm != 'sha256':
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_4(data: str, algorithm: str = 'sha256') -> str:
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
    if algorithm == 'XXsha256XX':
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_5(data: str, algorithm: str = 'sha256') -> str:
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
    if algorithm == 'SHA256':
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_6(data: str, algorithm: str = 'sha256') -> str:
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
        return hashlib.sha256(None).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_7(data: str, algorithm: str = 'sha256') -> str:
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
        return hashlib.sha256(data.encode(None)).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_8(data: str, algorithm: str = 'sha256') -> str:
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
        return hashlib.sha256(data.encode('XXutf-8XX')).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_9(data: str, algorithm: str = 'sha256') -> str:
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
        return hashlib.sha256(data.encode('UTF-8')).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_10(data: str, algorithm: str = 'sha256') -> str:
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
    elif algorithm != 'sha512':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_11(data: str, algorithm: str = 'sha256') -> str:
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
    elif algorithm == 'XXsha512XX':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_12(data: str, algorithm: str = 'sha256') -> str:
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
    elif algorithm == 'SHA512':
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_13(data: str, algorithm: str = 'sha256') -> str:
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
        return hashlib.sha512(None).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_14(data: str, algorithm: str = 'sha256') -> str:
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
        return hashlib.sha512(data.encode(None)).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_15(data: str, algorithm: str = 'sha256') -> str:
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
        return hashlib.sha512(data.encode('XXutf-8XX')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_16(data: str, algorithm: str = 'sha256') -> str:
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
        return hashlib.sha512(data.encode('UTF-8')).hexdigest()
    else:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'sha512'."
        )


def x_hash_secure__mutmut_17(data: str, algorithm: str = 'sha256') -> str:
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
            None
        )

x_hash_secure__mutmut_mutants : ClassVar[MutantDict] = {
'x_hash_secure__mutmut_1': x_hash_secure__mutmut_1, 
    'x_hash_secure__mutmut_2': x_hash_secure__mutmut_2, 
    'x_hash_secure__mutmut_3': x_hash_secure__mutmut_3, 
    'x_hash_secure__mutmut_4': x_hash_secure__mutmut_4, 
    'x_hash_secure__mutmut_5': x_hash_secure__mutmut_5, 
    'x_hash_secure__mutmut_6': x_hash_secure__mutmut_6, 
    'x_hash_secure__mutmut_7': x_hash_secure__mutmut_7, 
    'x_hash_secure__mutmut_8': x_hash_secure__mutmut_8, 
    'x_hash_secure__mutmut_9': x_hash_secure__mutmut_9, 
    'x_hash_secure__mutmut_10': x_hash_secure__mutmut_10, 
    'x_hash_secure__mutmut_11': x_hash_secure__mutmut_11, 
    'x_hash_secure__mutmut_12': x_hash_secure__mutmut_12, 
    'x_hash_secure__mutmut_13': x_hash_secure__mutmut_13, 
    'x_hash_secure__mutmut_14': x_hash_secure__mutmut_14, 
    'x_hash_secure__mutmut_15': x_hash_secure__mutmut_15, 
    'x_hash_secure__mutmut_16': x_hash_secure__mutmut_16, 
    'x_hash_secure__mutmut_17': x_hash_secure__mutmut_17
}

def hash_secure(*args, **kwargs):
    result = _mutmut_trampoline(x_hash_secure__mutmut_orig, x_hash_secure__mutmut_mutants, args, kwargs)
    return result 

hash_secure.__signature__ = _mutmut_signature(x_hash_secure__mutmut_orig)
x_hash_secure__mutmut_orig.__name__ = 'x_hash_secure'


def x_mask_sensitive__mutmut_orig(value: str, show_chars: int = 4) -> str:
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


def x_mask_sensitive__mutmut_1(value: str, show_chars: int = 5) -> str:
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


def x_mask_sensitive__mutmut_2(value: str, show_chars: int = 4) -> str:
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
    if value:
        return ""
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    return f"{value[:show_chars]}***{value[-show_chars:]}"


def x_mask_sensitive__mutmut_3(value: str, show_chars: int = 4) -> str:
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
        return "XXXX"
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    return f"{value[:show_chars]}***{value[-show_chars:]}"


def x_mask_sensitive__mutmut_4(value: str, show_chars: int = 4) -> str:
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
    if len(value) < show_chars * 2:
        return "*" * len(value)
    return f"{value[:show_chars]}***{value[-show_chars:]}"


def x_mask_sensitive__mutmut_5(value: str, show_chars: int = 4) -> str:
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
    if len(value) <= show_chars / 2:
        return "*" * len(value)
    return f"{value[:show_chars]}***{value[-show_chars:]}"


def x_mask_sensitive__mutmut_6(value: str, show_chars: int = 4) -> str:
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
    if len(value) <= show_chars * 3:
        return "*" * len(value)
    return f"{value[:show_chars]}***{value[-show_chars:]}"


def x_mask_sensitive__mutmut_7(value: str, show_chars: int = 4) -> str:
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
        return "*" / len(value)
    return f"{value[:show_chars]}***{value[-show_chars:]}"


def x_mask_sensitive__mutmut_8(value: str, show_chars: int = 4) -> str:
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
        return "XX*XX" * len(value)
    return f"{value[:show_chars]}***{value[-show_chars:]}"


def x_mask_sensitive__mutmut_9(value: str, show_chars: int = 4) -> str:
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
    return f"{value[:show_chars]}***{value[+show_chars:]}"

x_mask_sensitive__mutmut_mutants : ClassVar[MutantDict] = {
'x_mask_sensitive__mutmut_1': x_mask_sensitive__mutmut_1, 
    'x_mask_sensitive__mutmut_2': x_mask_sensitive__mutmut_2, 
    'x_mask_sensitive__mutmut_3': x_mask_sensitive__mutmut_3, 
    'x_mask_sensitive__mutmut_4': x_mask_sensitive__mutmut_4, 
    'x_mask_sensitive__mutmut_5': x_mask_sensitive__mutmut_5, 
    'x_mask_sensitive__mutmut_6': x_mask_sensitive__mutmut_6, 
    'x_mask_sensitive__mutmut_7': x_mask_sensitive__mutmut_7, 
    'x_mask_sensitive__mutmut_8': x_mask_sensitive__mutmut_8, 
    'x_mask_sensitive__mutmut_9': x_mask_sensitive__mutmut_9
}

def mask_sensitive(*args, **kwargs):
    result = _mutmut_trampoline(x_mask_sensitive__mutmut_orig, x_mask_sensitive__mutmut_mutants, args, kwargs)
    return result 

mask_sensitive.__signature__ = _mutmut_signature(x_mask_sensitive__mutmut_orig)
x_mask_sensitive__mutmut_orig.__name__ = 'x_mask_sensitive'


def x_sanitize_url__mutmut_orig(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_1(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_2(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return True
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_3(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = None
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_4(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(None)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_5(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = None
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_6(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.upper()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_7(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if 'XX:XX' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_8(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' not in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_9(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = None
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_10(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(None, 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_11(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', None)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_12(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_13(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', )[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_14(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.rsplit(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_15(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split('XX:XX', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_16(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 2)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_17(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[1]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_18(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is not None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_19(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(None)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_20(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = None
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_21(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.upper()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_22(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower and netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_23(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc != allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_24(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith(None):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_25(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' - allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_26(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('XX.XX' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_27(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return False
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_28(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return True
    except Exception:
        # If URL parsing fails, consider it invalid
        return False


def x_sanitize_url__mutmut_29(url: str, allowed_domains: Optional[list[str]] = None) -> bool:
    """
    Validate that a URL belongs to an allowed domain.
    
    This function prevents URL substring sanitization vulnerabilities by
    properly parsing the URL and checking the domain component, not just
    searching for the domain string anywhere in the URL.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names (e.g., ['example.com', 'api.example.com'])
                        If None, returns True for any valid URL with a domain.
    
    Returns:
        True if URL is from an allowed domain, False otherwise
    
    Example:
        >>> sanitize_url("http://example.com/path", ["example.com"])
        True
        >>> sanitize_url("http://evil.com/example.com", ["example.com"])
        False
        >>> sanitize_url("http://example.com.evil.com", ["example.com"])
        False
        >>> sanitize_url("http://evilexample.com", ["example.com"])
        False
    
    Security Note:
        This prevents attacks where malicious URLs contain the allowed domain
        as a substring in the path, query parameters, or as part of a different
        domain name.
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in netloc:
            netloc = netloc.split(':', 1)[0]
        
        # If no allowed domains specified, just check that we have a valid domain
        if allowed_domains is None:
            return bool(netloc)
        
        # Check if domain matches exactly or is a subdomain
        for allowed_domain in allowed_domains:
            allowed_lower = allowed_domain.lower()
            if netloc == allowed_lower or netloc.endswith('.' + allowed_lower):
                return True
        
        return False
    except Exception:
        # If URL parsing fails, consider it invalid
        return True

x_sanitize_url__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_url__mutmut_1': x_sanitize_url__mutmut_1, 
    'x_sanitize_url__mutmut_2': x_sanitize_url__mutmut_2, 
    'x_sanitize_url__mutmut_3': x_sanitize_url__mutmut_3, 
    'x_sanitize_url__mutmut_4': x_sanitize_url__mutmut_4, 
    'x_sanitize_url__mutmut_5': x_sanitize_url__mutmut_5, 
    'x_sanitize_url__mutmut_6': x_sanitize_url__mutmut_6, 
    'x_sanitize_url__mutmut_7': x_sanitize_url__mutmut_7, 
    'x_sanitize_url__mutmut_8': x_sanitize_url__mutmut_8, 
    'x_sanitize_url__mutmut_9': x_sanitize_url__mutmut_9, 
    'x_sanitize_url__mutmut_10': x_sanitize_url__mutmut_10, 
    'x_sanitize_url__mutmut_11': x_sanitize_url__mutmut_11, 
    'x_sanitize_url__mutmut_12': x_sanitize_url__mutmut_12, 
    'x_sanitize_url__mutmut_13': x_sanitize_url__mutmut_13, 
    'x_sanitize_url__mutmut_14': x_sanitize_url__mutmut_14, 
    'x_sanitize_url__mutmut_15': x_sanitize_url__mutmut_15, 
    'x_sanitize_url__mutmut_16': x_sanitize_url__mutmut_16, 
    'x_sanitize_url__mutmut_17': x_sanitize_url__mutmut_17, 
    'x_sanitize_url__mutmut_18': x_sanitize_url__mutmut_18, 
    'x_sanitize_url__mutmut_19': x_sanitize_url__mutmut_19, 
    'x_sanitize_url__mutmut_20': x_sanitize_url__mutmut_20, 
    'x_sanitize_url__mutmut_21': x_sanitize_url__mutmut_21, 
    'x_sanitize_url__mutmut_22': x_sanitize_url__mutmut_22, 
    'x_sanitize_url__mutmut_23': x_sanitize_url__mutmut_23, 
    'x_sanitize_url__mutmut_24': x_sanitize_url__mutmut_24, 
    'x_sanitize_url__mutmut_25': x_sanitize_url__mutmut_25, 
    'x_sanitize_url__mutmut_26': x_sanitize_url__mutmut_26, 
    'x_sanitize_url__mutmut_27': x_sanitize_url__mutmut_27, 
    'x_sanitize_url__mutmut_28': x_sanitize_url__mutmut_28, 
    'x_sanitize_url__mutmut_29': x_sanitize_url__mutmut_29
}

def sanitize_url(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_url__mutmut_orig, x_sanitize_url__mutmut_mutants, args, kwargs)
    return result 

sanitize_url.__signature__ = _mutmut_signature(x_sanitize_url__mutmut_orig)
x_sanitize_url__mutmut_orig.__name__ = 'x_sanitize_url'


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
    'sanitize_url',
    # Hashing functions
    'hash_secure',
]
