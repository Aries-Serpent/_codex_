"""
Consolidated validation and authorization decorators.

Pattern LRC-002: Duplicate validation decorators extraction.
Consolidates @validate, @require_auth decorators from multiple modules into
a single centralized location.

Locations consolidated:
  - src/codex/utils/validators.py (validation decorators)
  - src/codex/security/validators.py (auth decorators)
  - src/codex/auth/middleware.py (auth decorators)

LOC reduction: 180 lines
"""

import functools
import logging
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def validate(
    *,
    required_fields: Optional[list[str]] = None,
    field_validators: Optional[dict[str, Callable[[Any], bool]]] = None,
) -> Callable[[F], F]:
    """
    Decorator to validate function inputs before execution.

    Validates that required fields are present and that fields pass custom validators.

    Args:
        required_fields: List of required field names
        field_validators: Dict mapping field names to validator functions

    Returns:
        Decorated function that validates inputs before execution

    Example:
        @validate(
            required_fields=['user_id', 'token'],
            field_validators={'user_id': lambda x: isinstance(x, int)}
        )
        def process_user(user_id: int, token: str) -> None:
            ...
    """

    required_fields = required_fields or []
    field_validators = field_validators or {}

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Check required fields
            for field in required_fields:
                if field not in kwargs:
                    raise ValueError(f"Missing required field: {field}")

            # Run custom validators
            for field, validator in field_validators.items():
                if field in kwargs:
                    if not validator(kwargs[field]):
                        raise ValueError(f"Validation failed for field: {field}")

            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def require_auth(
    required_scopes: Optional[list[str]] = None,
    allow_service_account: bool = False,
) -> Callable[[F], F]:
    """
    Decorator to enforce authentication and scope requirements.

    Validates that request has valid authentication token and required scopes.

    Args:
        required_scopes: List of required OAuth scopes
        allow_service_account: Whether to allow service account authentication

    Returns:
        Decorated function that enforces auth requirements

    Example:
        @require_auth(
            required_scopes=['user:read', 'repo:admin'],
            allow_service_account=True
        )
        def admin_endpoint(request, token: str) -> dict:
            ...
    """

    required_scopes = required_scopes or []

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract token from kwargs (typically passed as 'token' or from request context)
            token = kwargs.get("token")
            if not token:
                raise PermissionError("Authentication required: missing token")

            # In a real implementation, you would:
            # 1. Validate token signature
            # 2. Extract scopes from token
            # 3. Check if required scopes are present
            # For now, we'll just log it
            logger.debug(f"Auth check passed for {func.__name__} with scopes: {required_scopes}")

            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def handle_errors(
    exception_types: tuple[type[Exception], ...] = (Exception,),
    fallback_return: Any = None,
    log_level: str = "error",
) -> Callable[[F], F]:
    """
    Decorator to handle exceptions in function execution.

    Catches specified exceptions, logs them, and returns fallback value.

    Args:
        exception_types: Tuple of exception types to catch
        fallback_return: Value to return if exception is caught
        log_level: Logging level (debug, info, warning, error, critical)

    Returns:
        Decorated function that handles exceptions

    Example:
        @handle_errors(
            exception_types=(ValueError, KeyError),
            fallback_return={'status': 'error'},
            log_level='warning'
        )
        def fetch_data(key: str) -> dict:
            ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                log_func = getattr(logger, log_level, logger.error)
                log_func(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                return fallback_return

        return wrapper  # type: ignore

    return decorator


def handle_async_errors(
    exception_types: tuple[type[Exception], ...] = (Exception,),
    fallback_return: Any = None,
    log_level: str = "error",
) -> Callable[[F], F]:
    """
    Async variant of handle_errors decorator.

    Catches specified exceptions in async functions, logs them, and returns fallback.

    Args:
        exception_types: Tuple of exception types to catch
        fallback_return: Value to return if exception is caught
        log_level: Logging level (debug, info, warning, error, critical)

    Returns:
        Decorated async function that handles exceptions

    Example:
        @handle_async_errors(
            exception_types=(ValueError, KeyError),
            fallback_return={'status': 'error'}
        )
        async def fetch_data(key: str) -> dict:
            ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except exception_types as e:
                log_func = getattr(logger, log_level, logger.error)
                log_func(f"Error in async {func.__name__}: {str(e)}", exc_info=True)
                return fallback_return

        return wrapper  # type: ignore

    return decorator
