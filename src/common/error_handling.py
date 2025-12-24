"""
Standardized error handling utilities for _codex_ project.
"""
import logging
from typing import Optional, Type, Tuple, Any
from functools import wraps

logger = logging.getLogger(__name__)


def safe_execute(
    operation_name: str,
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Optional[Any] = None,
    log_level: str = "warning"
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
                log_method(
                    f"{operation_name} failed in {func.__name__}: {exc}",
                    exc_info=True
                )
                return default_return
        return wrapper
    return decorator
