"""
Standardized error handling utilities for _codex_ project.
"""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

logger = logging.getLogger(__name__)


def safe_execute(
    operation_name: str,
    exception_types: tuple[type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
):
    """
    Decorator for safe operation execution with proper error logging.

    Args:
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as exc:
                log_method = getattr(logger, log_level)
                log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
                return default_return

        return wrapper

    return decorator


def safe_call(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    exception_types: tuple[type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning",
    **kwargs,
) -> Any:
    """
    Inline function for safe operation execution with proper error logging.

    Args:
        func: Function to execute safely
        *args: Positional arguments to pass to func
        operation_name: Human-readable operation description
        exception_types: Tuple of exception types to catch
        default_return: Value to return on exception
        log_level: Logging level (debug, info, warning, error, critical)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func or default_return on exception

    Example:
        result = safe_call(risky_operation, arg1, arg2,
                          operation_name="risky operation",
                          default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except exception_types as exc:
        log_method = getattr(logger, log_level)
        log_method(f"{operation_name} failed in {func.__name__}: {exc}", exc_info=True)
        return default_return
