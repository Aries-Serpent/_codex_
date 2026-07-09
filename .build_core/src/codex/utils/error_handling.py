"""
P003/P004: Error Handling & Logging Utilities

Consolidates 4,545 occurrences of exception handling and
1,706 occurrences of error logging patterns.

Example:
    # Instead of: try/except/log pattern
    with error_context("loading config"):
        config = load_config()

    # Instead of: logger.error(...) scattered everywhere
    log_error(exc, "config loading failed")
"""

import logging
from contextlib import contextmanager
from typing import Callable, Optional, Tuple, TypeVar

__all__ = [
    "log_error",
    "log_warning",
    "error_context",
    "ErrorChain",
    "handle_error",
    "ErrorLoggingError",
]

T = TypeVar("T")
logger = logging.getLogger(__name__)


class ErrorLoggingError(Exception):
    """Raised by error handling utilities."""

    pass


def log_error(
    exc: Exception,
    context: Optional[str] = None,
    level: int = logging.ERROR,
) -> None:
    """
    Log an exception with optional context.

    Args:
        exc: Exception to log
        context: Context description
        level: Logging level

    Example:
        >>> try:
        ...     do_something()
        ... except Exception as e:
        ...     log_error(e, "during initialization")
    """
    if context:
        logger.log(level, f"{context}: {exc}", exc_info=exc)
    else:
        logger.log(level, str(exc), exc_info=exc)


def log_warning(
    message: str,
    context: Optional[str] = None,
) -> None:
    """
    Log a warning message.

    Args:
        message: Warning message
        context: Context description
    """
    if context:
        logger.warning(f"{context}: {message}")
    else:
        logger.warning(message)


def handle_error(
    exc: Exception,
    handler: Optional[Callable[[Exception], None]] = None,
    reraise: bool = False,
) -> None:
    """
    Handle an exception with optional custom handler.

    Args:
        exc: Exception to handle
        handler: Optional custom handler function
        reraise: If True, reraise after handling

    Raises:
        Exception: If reraise=True
    """
    log_error(exc)
    if handler:
        handler(exc)
    if reraise:
        raise


@contextmanager
def error_context(name: str):
    """
    Context manager for automatic error logging with context.

    Args:
        name: Context description

    Example:
        >>> with error_context("database connection"):
        ...     connect_to_db()
    """
    try:
        yield
    except Exception as exc:
        log_error(exc, context=name)
        raise


class ErrorChain:
    """Chain exceptions together with context."""

    def __init__(self, initial_exc: Exception, context: str = ""):
        self.exceptions: Tuple[Exception, ...] = (initial_exc,)
        self.context = context

    def chain(self, exc: Exception, context: str = "") -> "ErrorChain":
        """Add an exception to the chain."""
        self.exceptions = self.exceptions + (exc,)
        if context:
            self.context += f" -> {context}"
        return self

    def raise_chained(self) -> None:
        """Raise the final exception with chain context."""
        final_exc = self.exceptions[-1]
        if self.context:
            raise final_exc from self.exceptions[0]
        raise final_exc
