"""Security hardening utilities for Phase 3 enhanced security.

This module provides:
1. Secure subprocess execution with input validation
2. Secure exception handling with logging
3. Security-aware random number generation
4. Input validation and sanitization
5. Security event logging and audit trails
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable, Optional, Sequence, TypeVar

import structlog

# Configure structured logging
logger = structlog.get_logger(__name__)
fallback_logger = logging.getLogger(__name__)

T = TypeVar("T")

# Security configuration
MAX_COMMAND_LENGTH = 10000
MAX_ARGS_PER_COMMAND = 100
SECURE_SUBPROCESS_TIMEOUT = 30  # seconds


class SecurityException(Exception):
    """Base exception for security violations."""

    pass


class SubprocessSecurityError(SecurityException):
    """Subprocess command failed security validation."""

    pass


class InputValidationError(SecurityException):
    """Input validation failed."""

    pass


def _log_security_event(
    event_type: str,
    severity: str = "INFO",
    **context: Any,
) -> None:
    """Log security event with structured context.

    Parameters
    ----------
    event_type : str
        Type of security event (e.g., "subprocess_execution", "input_validation")
    severity : str
        Severity level: INFO, WARNING, CRITICAL
    **context
        Additional context to log (without sensitive data)
    """
    log_data = {
        "event_type": event_type,
        "severity": severity,
        **context,
    }

    # Use structlog with fallback to standard logging
    try:
        if severity == "CRITICAL":
            logger.critical(f"Security event: {event_type}", **log_data)
        elif severity == "WARNING":
            logger.warning(f"Security event: {event_type}", **log_data)
        else:
            logger.info(f"Security event: {event_type}", **log_data)
    except Exception:
        # Fallback to standard logging
        msg = f"Security event {event_type}: {context}"
        if severity == "CRITICAL":
            fallback_logger.critical(msg, exc_info=True)
        elif severity == "WARNING":
            fallback_logger.warning(msg)
        else:
            fallback_logger.info(msg)


def validate_subprocess_command(
    cmd: Sequence[str] | str,
    allowed_executables: Optional[set[str]] = None,
    max_command_length: int = MAX_COMMAND_LENGTH,
    max_args: int = MAX_ARGS_PER_COMMAND,
) -> list[str]:
    """Validate subprocess command for security.

    Parameters
    ----------
    cmd : Sequence[str] | str
        Command as list or string (will be rejected if string)
    allowed_executables : Optional[set[str]]
        Whitelist of allowed executables. If None, common safe tools are allowed.
    max_command_length : int
        Maximum total command length
    max_args : int
        Maximum number of arguments

    Returns
    -------
    list[str]
        Validated command as list

    Raises
    ------
    SubprocessSecurityError
        If command fails validation
    """
    # Security Rule 1: Never accept shell=True with user input
    if isinstance(cmd, str):
        raise SubprocessSecurityError(
            "Command must be a list, not a string. "
            "This prevents shell injection attacks."
        )

    if not isinstance(cmd, (list, tuple)):
        raise SubprocessSecurityError(f"Command must be list or tuple, got {type(cmd)}")

    if len(cmd) == 0:
        raise SubprocessSecurityError("Command cannot be empty")

    if len(cmd) > max_args:
        raise SubprocessSecurityError(
            f"Command has {len(cmd)} args, max is {max_args}"
        )

    # Security Rule 2: Validate command length to prevent DOS
    total_length = sum(len(str(arg)) for arg in cmd)
    if total_length > max_command_length:
        raise SubprocessSecurityError(
            f"Command length {total_length} exceeds max {max_command_length}"
        )

    # Convert to list for consistency
    cmd_list = list(cmd)
    executable = cmd_list[0]

    # Security Rule 3: Check if executable is in whitelist
    if allowed_executables is not None:
        if executable not in allowed_executables and not Path(executable).is_absolute():
            raise SubprocessSecurityError(
                f"Executable '{executable}' not in allowed list"
            )

    # Security Rule 4: Prevent shell metacharacters in arguments
    dangerous_chars = {'$', '`', '|', '&', ';', '<', '>', '(', ')'}
    for arg in cmd_list[1:]:  # Skip executable
        arg_str = str(arg)
        if any(char in arg_str for char in dangerous_chars):
            _log_security_event(
                "potentially_dangerous_subprocess_arg",
                severity="WARNING",
                executable=executable,
                arg_length=len(arg_str),
            )

    _log_security_event(
        "subprocess_validation_passed",
        executable=executable,
        arg_count=len(cmd_list),
    )

    return cmd_list


def secure_subprocess_run(
    cmd: Sequence[str],
    *,
    timeout: int = SECURE_SUBPROCESS_TIMEOUT,
    input_data: Optional[str] = None,
    allowed_executables: Optional[set[str]] = None,
    check: bool = False,
    **kwargs: Any,
) -> subprocess.CompletedProcess:
    """Execute subprocess securely with validation and error handling.

    Parameters
    ----------
    cmd : Sequence[str]
        Command as list of strings
    timeout : int
        Timeout in seconds
    input_data : Optional[str]
        Input to send to subprocess
    allowed_executables : Optional[set[str]]
        Whitelist of allowed executables
    check : bool
        Whether to raise on non-zero exit
    **kwargs
        Additional arguments to subprocess.run()

    Returns
    -------
    subprocess.CompletedProcess
        Result of subprocess execution

    Raises
    ------
    SubprocessSecurityError
        If command fails validation
    subprocess.CalledProcessError
        If check=True and process exits with non-zero code
    subprocess.TimeoutExpired
        If process exceeds timeout
    """
    # Validate command
    validated_cmd = validate_subprocess_command(
        cmd, allowed_executables=allowed_executables
    )

    # Ensure safe execution parameters
    # Never allow shell=True
    if kwargs.get("shell", False):
        raise SubprocessSecurityError("shell=True is not permitted")

    # Use safe defaults
    run_kwargs = {
        "capture_output": True,
        "text": True,
        "timeout": timeout,
        "check": check,
        **kwargs,
    }

    try:
        _log_security_event(
            "subprocess_execution_start",
            executable=validated_cmd[0],
            arg_count=len(validated_cmd),
        )

        result = subprocess.run(validated_cmd, input=input_data, **run_kwargs)

        _log_security_event(
            "subprocess_execution_complete",
            executable=validated_cmd[0],
            returncode=result.returncode,
            has_stderr=bool(result.stderr),
        )

        return result

    except subprocess.TimeoutExpired:
        _log_security_event(
            "subprocess_timeout",
            severity="WARNING",
            executable=validated_cmd[0],
            timeout=timeout,
        )
        raise

    except subprocess.CalledProcessError as exc:
        _log_security_event(
            "subprocess_error",
            severity="WARNING",
            executable=validated_cmd[0],
            returncode=exc.returncode,
        )
        raise

    except Exception as exc:
        _log_security_event(
            "subprocess_unexpected_error",
            severity="CRITICAL",
            executable=validated_cmd[0],
            error_type=type(exc).__name__,
        )
        raise SubprocessSecurityError(f"Unexpected error executing subprocess: {exc}") from exc


def secure_exception_handler(
    func: Callable[..., T],
    *args: Any,
    fallback: Optional[T] = None,
    log_traceback: bool = True,
    **kwargs: Any,
) -> T | None:
    """Execute function with secure exception handling and logging.

    Parameters
    ----------
    func : Callable
        Function to execute
    *args
        Positional arguments
    fallback : Optional[T]
        Fallback value if function raises exception
    log_traceback : bool
        Whether to log full traceback
    **kwargs
        Keyword arguments

    Returns
    -------
    T | None
        Function result or fallback value

    Raises
    ------
    Never raises exceptions; logs and returns fallback
    """
    try:
        result = func(*args, **kwargs)
        _log_security_event(
            "function_execution_success",
            function=func.__name__,
        )
        return result

    except Exception as exc:
        _log_security_event(
            "function_execution_error",
            severity="WARNING",
            function=func.__name__,
            error_type=type(exc).__name__,
            error_msg=str(exc),
            has_traceback=log_traceback,
        )

        if log_traceback:
            fallback_logger.exception(
                f"Error in {func.__name__}", exc_info=True
            )

        return fallback


def validate_input_string(
    value: str,
    *,
    max_length: int = 10000,
    pattern: Optional[str] = None,
    allowed_chars: Optional[str] = None,
) -> str:
    """Validate input string for security.

    Parameters
    ----------
    value : str
        Input string to validate
    max_length : int
        Maximum allowed length
    pattern : Optional[str]
        Regex pattern that value must match
    allowed_chars : Optional[str]
        Set of allowed characters

    Returns
    -------
    str
        Validated string

    Raises
    ------
    InputValidationError
        If validation fails
    """
    if not isinstance(value, str):
        raise InputValidationError(f"Expected string, got {type(value)}")

    if len(value) > max_length:
        raise InputValidationError(f"String exceeds max length {max_length}")

    if pattern is not None:
        if not re.match(pattern, value):
            raise InputValidationError("String does not match required pattern")

    if allowed_chars is not None:
        for char in value:
            if char not in allowed_chars:
                raise InputValidationError(
                    f"String contains disallowed character: {repr(char)}"
                )

    return value


def validate_file_path(
    path: str | Path,
    *,
    base_dir: Optional[str | Path] = None,
    must_exist: bool = False,
    is_directory: bool = False,
) -> Path:
    """Validate file path for security.

    Parameters
    ----------
    path : str | Path
        Path to validate
    base_dir : Optional[str | Path]
        Base directory for relative paths
    must_exist : bool
        Whether path must exist
    is_directory : bool
        Whether path must be a directory

    Returns
    -------
    Path
        Validated path

    Raises
    ------
    InputValidationError
        If validation fails
    """
    try:
        path_obj = Path(path).resolve()

        # Security: Prevent path traversal
        if base_dir is not None:
            base_path = Path(base_dir).resolve()
            try:
                path_obj.relative_to(base_path)
            except ValueError:
                raise InputValidationError(
                    "Path escapes base directory (path traversal attempt)"
                )

        if must_exist and not path_obj.exists():
            raise InputValidationError(f"Path does not exist: {path_obj}")

        if is_directory:
            if must_exist and not path_obj.is_dir():
                raise InputValidationError(f"Path is not a directory: {path_obj}")

        return path_obj

    except Exception as exc:
        if isinstance(exc, InputValidationError):
            raise
        raise InputValidationError(f"Invalid path: {exc}") from exc


def sanitize_for_logging(value: Any, max_length: int = 1000) -> str:
    """Sanitize value for logging (remove sensitive data).

    Parameters
    ----------
    value : Any
        Value to sanitize
    max_length : int
        Maximum output length

    Returns
    -------
    str
        Sanitized string suitable for logging
    """
    value_str = str(value)

    # Redact common sensitive patterns
    redacted = re.sub(
        r"(api[_-]?key|password|token|secret|authorization)=[^&\s]+",
        r"\1=***REDACTED***",
        value_str,
        flags=re.IGNORECASE,
    )

    # Truncate if too long
    if len(redacted) > max_length:
        redacted = redacted[:max_length] + "..."

    return redacted


def get_secure_random_int(
    *,
    min_value: int = 0,
    max_value: int = 2**31 - 1,
    context: str = "general",
) -> int:
    """Generate cryptographically secure random integer.

    Use this instead of random.randint() for security-sensitive operations.

    Parameters
    ----------
    min_value : int
        Minimum value (inclusive)
    max_value : int
        Maximum value (inclusive)
    context : str
        Context/purpose for logging

    Returns
    -------
    int
        Random integer

    Raises
    ------
    InputValidationError
        If min_value >= max_value
    """
    if min_value >= max_value:
        raise InputValidationError(f"min_value {min_value} must be < max_value {max_value}")

    _log_security_event(
        "secure_random_generation",
        context=context,
        min_value=min_value,
        max_value=max_value,
    )

    # Use os.urandom for cryptographic strength
    range_size = max_value - min_value + 1
    random_bytes = os.urandom(4)
    random_int = int.from_bytes(random_bytes, byteorder="big") % range_size
    return min_value + random_int


def is_security_critical(context: str) -> bool:
    """Determine if context is security-critical.

    Parameters
    ----------
    context : str
        Context/purpose of operation

    Returns
    -------
    bool
        True if operation is security-critical
    """
    security_keywords = {
        "auth",
        "crypto",
        "key",
        "token",
        "password",
        "secret",
        "permission",
        "rbac",
        "rbac_engine",
    }
    return any(keyword in context.lower() for keyword in security_keywords)


# Common safe executables for subprocess validation
SAFE_EXECUTABLES = {
    "git",
    "python",
    "python3",
    "bash",
    "sh",
    "grep",
    "find",
    "ls",
    "cat",
    "echo",
    "ffmpeg",
    "ffprobe",
}


__all__ = [
    "SecurityException",
    "SubprocessSecurityError",
    "InputValidationError",
    "validate_subprocess_command",
    "secure_subprocess_run",
    "secure_exception_handler",
    "validate_input_string",
    "validate_file_path",
    "sanitize_for_logging",
    "get_secure_random_int",
    "is_security_critical",
    "SAFE_EXECUTABLES",
]
