"""
Safe parameterized logging module to prevent log injection attacks.

This module provides a wrapper around Python's logging module that ensures
all dynamic content is properly sanitized before being included in log messages.

CWE-117: Log Injection Prevention
Security Model:
- All log messages are parameterized to prevent injection
- Dynamic values use %s formatting with logger's built-in formatting
- Control characters and newlines are stripped from all parameters
- Structured logging with JSON-safe formats

Usage:
    from codex.logging_safe import create_safe_logger
    
    logger = create_safe_logger(__name__)
    logger.info("User login", {"username": user_input, "status": "success"})
"""

import json
import logging
import re
from typing import Any, Optional


def _sanitize_value(value: Any, max_length: int = 1000) -> str:
    """
    Sanitize a single value for safe logging.
    
    Removes control characters that could be used for log injection:
    - Newlines (\\n, \\r)
    - Tabs (\\t)
    - Bell, backspace, form feed characters
    - Other C0 and C1 control characters
    - ANSI escape sequences
    
    Args:
        value: Value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 1000)
    
    Returns:
        Safe string representation
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_val = str(value)
    
    # Remove ANSI escape codes
    str_val = re.sub(r"\x1b\[[0-9;]*[mGHJ]", "", str_val)
    str_val = re.sub(r"\[[0-9;]*m", "", str_val)
    
    # Remove control characters (newlines, tabs, control chars)
    # Keep printable ASCII and extended ASCII
    str_val = re.sub(r"[\n\r\t\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]", "", str_val)
    
    # Truncate if too long to prevent DoS
    if len(str_val) > max_length:
        str_val = str_val[:max_length] + "...[truncated]"
    
    return str_val


class SafeLogger:
    """
    Wrapper around Python's logger that sanitizes all dynamic content.
    
    Uses parameterized logging with %s formatting to prevent injection attacks.
    All user-controlled data is automatically sanitized.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize SafeLogger.
        
        Args:
            logger: Python logging.Logger instance to wrap
        """
        self._logger = logger
    
    def _format_extra(self, extra: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Format extra fields for structured logging.
        
        Args:
            extra: Extra fields to include in log record
        
        Returns:
            Extra dict with sanitized values
        """
        if not extra:
            return {}
        
        sanitized = {}
        for key, value in extra.items():
            if key.startswith('_'):
                continue
            sanitized[key] = _sanitize_value(value)
        
        return sanitized
    
    def _sanitize_args(self, *args: Any) -> tuple[Any, ...]:
        """
        Sanitize all positional arguments for log formatting.
        
        Args:
            *args: Positional arguments to sanitize
        
        Returns:
            Tuple of sanitized arguments
        """
        return tuple(_sanitize_value(arg) if not isinstance(arg, (int, float, bool)) else arg 
                    for arg in args)
    
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message with sanitized arguments."""
        args = self._sanitize_args(*args)
        extra = self._format_extra(kwargs.pop('extra', None))
        if extra:
            kwargs['extra'] = extra
        self._logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log info message with sanitized arguments."""
        args = self._sanitize_args(*args)
        extra = self._format_extra(kwargs.pop('extra', None))
        if extra:
            kwargs['extra'] = extra
        self._logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message with sanitized arguments."""
        args = self._sanitize_args(*args)
        extra = self._format_extra(kwargs.pop('extra', None))
        if extra:
            kwargs['extra'] = extra
        self._logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log error message with sanitized arguments."""
        args = self._sanitize_args(*args)
        extra = self._format_extra(kwargs.pop('extra', None))
        if extra:
            kwargs['extra'] = extra
        self._logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log critical message with sanitized arguments."""
        args = self._sanitize_args(*args)
        extra = self._format_extra(kwargs.pop('extra', None))
        if extra:
            kwargs['extra'] = extra
        self._logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log exception with sanitized arguments."""
        args = self._sanitize_args(*args)
        extra = self._format_extra(kwargs.pop('extra', None))
        if extra:
            kwargs['extra'] = extra
        self._logger.exception(msg, *args, **kwargs)
    
    # Aliases
    def warn(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Deprecated alias for warning()."""
        self.warning(msg, *args, **kwargs)
    
    def fatal(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Deprecated alias for critical()."""
        self.critical(msg, *args, **kwargs)
    
    # Proxy other attributes to underlying logger
    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to underlying logger."""
        return getattr(self._logger, name)


def create_safe_logger(name: str) -> SafeLogger:
    """
    Create a safe logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        SafeLogger instance wrapping logging.getLogger(name)
    
    Example:
        >>> logger = create_safe_logger(__name__)
        >>> logger.info("Processing user: %s", untrusted_username)
    """
    base_logger = logging.getLogger(name)
    return SafeLogger(base_logger)


def sanitize_for_log(value: Any) -> str:
    """
    Sanitize a value for safe inclusion in log messages.
    
    This is useful when you need to include dynamic values in log messages
    but cannot use parameterized formatting (e.g., in message templates).
    
    Args:
        value: Value to sanitize
    
    Returns:
        Safe string representation
    
    Example:
        >>> logger.info(f"Error: {sanitize_for_log(error_msg)}")
    """
    return _sanitize_value(value)


def create_safe_json_log(message: str, **fields: Any) -> str:
    """
    Create a JSON-formatted log message with sanitized fields.
    
    Useful for structured logging that integrates with log aggregation systems.
    
    Args:
        message: Main log message
        **fields: Additional fields to include in JSON
    
    Returns:
        JSON string with sanitized content
    
    Example:
        >>> log_entry = create_safe_json_log(
        ...     "User action",
        ...     user=username,
        ...     action="login",
        ...     status="success"
        ... )
        >>> logger.info(log_entry)
    """
    entry = {
        "message": _sanitize_value(message),
    }
    
    for key, value in fields.items():
        entry[key] = _sanitize_value(value)
    
    return json.dumps(entry)


__all__ = [
    "create_safe_logger",
    "sanitize_for_log",
    "create_safe_json_log",
    "SafeLogger",
]
