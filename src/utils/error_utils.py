"""
Error Handling Utilities

This module provides reusable error handling patterns and utilities.

Functions:
    - safe_call: Execute function safely with fallback
    - try_parse: Parse with fallback value
    - try_import: Safe module import
    - log_and_skip: Log error and continue
    - retry_with_backoff: Retry with exponential backoff

Author: Codex Team
"""

from __future__ import annotations

import importlib
import logging
import time
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def safe_call(
    func: Callable[..., T],
    *args: Any,
    default: Optional[T] = None,
    error_msg: Optional[str] = None,
    log_level: int = logging.WARNING,
    **kwargs: Any,
) -> Optional[T]:
    """
    Execute function safely with error handling.

    Args:
        func: Callable to execute
        *args: Positional arguments for func
        default: Default value if function raises exception
        error_msg: Custom error message to log
        log_level: Logging level for errors
        **kwargs: Keyword arguments for func

    Returns:
        Result of func or default if exception occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        msg = error_msg or f"Error calling {func.__name__}: {e}"
        logger.log(log_level, msg)
        return default


def try_parse(
    value: Any,
    parser: Callable[[Any], T],
    default: T,
    error_msg: Optional[str] = None,
) -> T:
    """
    Try to parse value with fallback to default.

    Args:
        value: Value to parse
        parser: Parsing function
        default: Default value if parsing fails
        error_msg: Custom error message

    Returns:
        Parsed value or default
    """
    try:
        return parser(value)
    except Exception as e:
        if error_msg:
            logger.warning(f"{error_msg}: {e}")
        return default


def try_import(
    module_path: str,
    attr_name: Optional[str] = None,
    default: Any = None,
) -> Any:
    """
    Safely import a module or attribute.

    Args:
        module_path: Path to module (e.g., "module.submodule")
        attr_name: Attribute name to import from module
        default: Default value if import fails

    Returns:
        Imported module/attribute or default
    """
    try:
        module = importlib.import_module(module_path)
        if attr_name:
            return getattr(module, attr_name, default)
        return module
    except (ImportError, AttributeError) as e:
        logger.debug(f"Failed to import {module_path}.{attr_name or ''}: {e}")
        return default


def log_and_skip(
    error: Exception,
    context: str,
    log_level: int = logging.WARNING,
) -> None:
    """
    Log error and continue (skip current item).

    Args:
        error: The exception that occurred
        context: Context description for logging
        log_level: Logging level to use
    """
    logger.log(log_level, f"Skipping {context}: {error}")


def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    initial_delay: float = 1.0,
    *args: Any,
    **kwargs: Any,
) -> Optional[T]:
    """
    Retry function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff
        initial_delay: Initial delay in seconds
        *args: Arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Result of func or None if all retries fail
    """
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt < max_retries - 1:
                logger.debug(
                    f"Attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {delay}s..."
                )
                time.sleep(delay)
                delay *= backoff_factor
            else:
                logger.warning(f"All {max_retries} attempts failed: {e}")

    return None


def chain_try(
    *funcs: tuple[Callable[..., T], tuple[Any, ...], dict[str, Any]],
    default: Optional[T] = None,
) -> Optional[T]:
    """
    Try multiple functions in sequence until one succeeds.

    Args:
        *funcs: Tuples of (func, args, kwargs) to try
        default: Default value if all fail

    Returns:
        Result of first successful function or default
    """
    for func, args, kwargs in funcs:
        result = safe_call(func, *args, **kwargs)
        if result is not None:
            return result
    return default
