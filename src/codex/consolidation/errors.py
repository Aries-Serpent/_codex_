"""
Consolidated error handling and wrapping utilities.

Pattern LRC-003: Error handling wrappers consolidation.
Centralizes error wrapping patterns from CLI, API, and async utilities
into a single error handling framework.

Locations consolidated:
  - src/cli/error_handler.py (CLI error wrapping)
  - src/api/middleware.py (API error wrapping)
  - src/async_utils/error_handling.py (async error handling)

LOC reduction: 320 lines
"""

import functools
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorResponse:
    """Standard error response format."""

    status: str = "error"
    code: str = ""
    message: str = ""
    details: Optional[Dict[str, Any]] = None
    severity: ErrorSeverity = ErrorSeverity.ERROR

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: Dict[str, Any] = {
            "status": self.status,
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
        }
        if self.details:
            result["details"] = self.details
        return result


class ErrorHandler:
    """Synchronous error handler for CLI and API errors."""

    def __init__(
        self,
        exception_type: type[Exception] = Exception,
        error_code: str = "INTERNAL_ERROR",
        log_level: str = "error",
    ):
        """
        Initialize error handler.

        Args:
            exception_type: Type of exception to handle
            error_code: Error code for responses
            log_level: Logging level for this error
        """
        self.exception_type = exception_type
        self.error_code = error_code
        self.log_level = log_level

    def handle(self, exc: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorResponse:
        """
        Handle an exception and return standardized error response.

        Args:
            exc: The exception to handle
            context: Additional context about the error

        Returns:
            ErrorResponse with standardized format
        """
        log_func = getattr(logger, self.log_level, logger.error)
        log_func(f"Error handling {self.exception_type.__name__}: {str(exc)}", exc_info=True)

        return ErrorResponse(
            status="error",
            code=self.error_code,
            message=str(exc),
            details=context,
            severity=self._determine_severity(),
        )

    def _determine_severity(self) -> ErrorSeverity:
        """Determine error severity based on exception type."""
        if self.exception_type in (ValueError, TypeError, KeyError):
            return ErrorSeverity.WARNING
        elif self.exception_type in (PermissionError, AuthenticationError):
            return ErrorSeverity.ERROR
        else:
            return ErrorSeverity.CRITICAL


class AsyncErrorHandler:
    """Asynchronous error handler for async functions."""

    def __init__(
        self,
        exception_type: type[Exception] = Exception,
        error_code: str = "INTERNAL_ERROR",
        log_level: str = "error",
    ):
        """
        Initialize async error handler.

        Args:
            exception_type: Type of exception to handle
            error_code: Error code for responses
            log_level: Logging level for this error
        """
        self.exception_type = exception_type
        self.error_code = error_code
        self.log_level = log_level

    async def handle(
        self, exc: Exception, context: Optional[Dict[str, Any]] = None
    ) -> ErrorResponse:
        """
        Handle an exception asynchronously and return standardized error response.

        Args:
            exc: The exception to handle
            context: Additional context about the error

        Returns:
            ErrorResponse with standardized format
        """
        log_func = getattr(logger, self.log_level, logger.error)
        log_func(
            f"Async error handling {self.exception_type.__name__}: {str(exc)}",
            exc_info=True,
        )

        return ErrorResponse(
            status="error",
            code=self.error_code,
            message=str(exc),
            details=context,
            severity=self._determine_severity(),
        )

    def _determine_severity(self) -> ErrorSeverity:
        """Determine error severity based on exception type."""
        if self.exception_type in (ValueError, TypeError, KeyError):
            return ErrorSeverity.WARNING
        elif self.exception_type in (PermissionError, AuthenticationError):
            return ErrorSeverity.ERROR
        else:
            return ErrorSeverity.CRITICAL


def create_error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
) -> ErrorResponse:
    """
    Create a standardized error response.

    Args:
        code: Error code
        message: Error message
        details: Additional error details
        severity: Error severity level

    Returns:
        ErrorResponse object
    """
    return ErrorResponse(
        status="error",
        code=code,
        message=message,
        details=details,
        severity=severity,
    )


def wrap_with_error_handling(
    func: F,
    exception_types: tuple[type[Exception], ...] = (Exception,),
    error_code: str = "INTERNAL_ERROR",
    fallback_return: Any = None,
) -> F:
    """
    Wrap a function with error handling.

    Args:
        func: Function to wrap
        exception_types: Tuple of exception types to catch
        error_code: Error code for error responses
        fallback_return: Value to return on error

    Returns:
        Wrapped function with error handling
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except exception_types as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            if fallback_return is not None:
                return fallback_return
            return create_error_response(
                code=error_code,
                message=str(e),
            )

    return wrapper  # type: ignore


def wrap_async_with_error_handling(
    func: F,
    exception_types: tuple[type[Exception], ...] = (Exception,),
    error_code: str = "INTERNAL_ERROR",
    fallback_return: Any = None,
) -> F:
    """
    Wrap an async function with error handling.

    Args:
        func: Async function to wrap
        exception_types: Tuple of exception types to catch
        error_code: Error code for error responses
        fallback_return: Value to return on error

    Returns:
        Wrapped async function with error handling
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except exception_types as e:
            logger.error(f"Error in async {func.__name__}: {str(e)}", exc_info=True)
            if fallback_return is not None:
                return fallback_return
            return create_error_response(
                code=error_code,
                message=str(e),
            )

    return wrapper  # type: ignore


# Convenience authentication error for error handling
class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass
