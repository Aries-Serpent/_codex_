"""Security decorators for scope-based authorization.

This module provides decorators for enforcing scope requirements
in API endpoints and service methods.

Part of PS-05 Enhancement: Scope Validation Library - Priority 4
"""

from __future__ import annotations

import functools
import logging
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any, Optional

from security.scope_validator import (
    ScopeValidator,
    TokenScope,
)

logger = logging.getLogger(__name__)

# Context variable for storing current request's scope validator
_scope_validator_context: ContextVar[Optional[ScopeValidator]] = ContextVar(
    "scope_validator", default=None
)


def set_scope_validator(validator: ScopeValidator) -> None:
    """Set scope validator for current request context.

    This should be called by middleware/dependency injection
    after extracting token scopes from the request.

    Args:
        validator: ScopeValidator instance for current request
    """
    _scope_validator_context.set(validator)


def get_scope_validator() -> Optional[ScopeValidator]:
    """Get scope validator from current request context.

    Returns:
        ScopeValidator instance or None if not set
    """
    return _scope_validator_context.get()


def clear_scope_validator() -> None:
    """Clear scope validator from current request context."""
    _scope_validator_context.set(None)


def require_scope(*required_scopes: str) -> Callable:
    """Decorator to require specific scopes for function execution.

    The decorated function will only execute if the current request
    has all required scopes. Otherwise, InsufficientScopeError is raised.

    Args:
        *required_scopes: Scope strings required (e.g., "repo:write", "workflow:read")

    Returns:
        Decorator function

    Raises:
        InsufficientScopeError: If token lacks required scopes
        RuntimeError: If no scope validator is set in context

    Example:
        >>> @require_scope("repo:write", "workflow:read")
        ... def update_workflow(workflow_id: str):
        ...     # Only executes if token has both scopes
        ...     pass
    """
    # Convert scope strings to TokenScope flags
    required_scope_flags = TokenScope.from_list(list(required_scopes))

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            validator = get_scope_validator()

            if validator is None:
                raise RuntimeError(
                    "No scope validator found in context. "
                    "Ensure middleware/dependency sets validator before calling."
                )

            # Check scope and raise if insufficient
            validator.require_scope(required_scope_flags)

            logger.debug(f"Scope check passed for {func.__name__}: {required_scopes}")

            # Execute function
            return func(*args, **kwargs)

        # Store metadata for introspection
        wrapper.__required_scopes__ = required_scopes  # type: ignore
        wrapper.__scope_protected__ = True  # type: ignore

        return wrapper

    return decorator


def require_any_scope(*required_scopes: str) -> Callable:
    """Decorator to require at least one of the specified scopes.

    The decorated function will only execute if the current request
    has at least one of the required scopes.

    Args:
        *required_scopes: Scope strings (at least one required)

    Returns:
        Decorator function

    Raises:
        InsufficientScopeError: If token lacks all required scopes
        RuntimeError: If no scope validator is set in context

    Example:
        >>> @require_any_scope("repo:write", "repo:admin")
        ... def modify_repository():
        ...     # Executes if token has either write or admin
        ...     pass
    """
    # Convert scope strings to TokenScope flags
    required_scope_flags = [TokenScope.from_string(scope) for scope in required_scopes]

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            validator = get_scope_validator()

            if validator is None:
                raise RuntimeError(
                    "No scope validator found in context. "
                    "Ensure middleware/dependency sets validator before calling."
                )

            # Check scope and raise if insufficient
            validator.require_any_scope(required_scope_flags)

            logger.debug(f"Scope check passed for {func.__name__}: one of {required_scopes}")

            # Execute function
            return func(*args, **kwargs)

        # Store metadata for introspection
        wrapper.__required_scopes__ = required_scopes  # type: ignore
        wrapper.__scope_protected__ = True  # type: ignore
        wrapper.__scope_any__ = True  # type: ignore

        return wrapper

    return decorator


def optional_scope(*scopes: str) -> Callable:
    """Decorator that checks scopes if validator is present, but doesn't require it.

    Useful for endpoints that behave differently based on permissions
    but don't strictly require them.

    Args:
        *scopes: Scope strings to check

    Returns:
        Decorator function

    Example:
        >>> @optional_scope("repo:write")
        ... def get_repository(repo_id: str):
        ...     validator = get_scope_validator()
        ...     if validator and validator.has_scope(TokenScope.WRITE_REPO):
        ...         # Return extra info for write access
        ...         return {"repo": repo_id, "write_access": True}
        ...     return {"repo": repo_id, "write_access": False}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            validator = get_scope_validator()

            if validator is not None:
                # Log scope check but don't enforce
                scope_flags = TokenScope.from_list(list(scopes))
                has_scopes = validator.has_scope(scope_flags)
                logger.debug(f"Optional scope check for {func.__name__}: {scopes} = {has_scopes}")

            # Execute function regardless
            return func(*args, **kwargs)

        # Store metadata
        wrapper.__optional_scopes__ = scopes  # type: ignore
        wrapper.__scope_optional__ = True  # type: ignore

        return wrapper

    return decorator


# FastAPI dependency injection helpers
try:
    from fastapi import (
        Depends,
        HTTPException,
        status,
    )
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    security = HTTPBearer()

    async def get_token_scopes(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> list[str]:
        """FastAPI dependency that extracts OAuth2/JWT scopes from a Bearer token.

        Uses ``TokenManager.validate_token()`` to verify the Bearer credential
        and returns the ``scopes`` claim from the validated payload.

        Behavior:
        - Returns an empty list (fail-closed) when ``CODEX_AUTH_SECRET`` is not
          set in the environment — the service will appear to have no scopes.
        - Raises HTTP 503 if the auth module is unavailable or the secret is
          missing.
        - Raises HTTP 401 with ``WWW-Authenticate: Bearer`` on expired tokens.
        - Raises HTTP 403 on any other validation failure.

        Environment:
            CODEX_AUTH_SECRET: Shared secret used to verify the JWT signature.
                Must be set via the application's settings or a secrets manager.

        Args:
            credentials: Bearer token extracted from the Authorization header
                by FastAPI's ``HTTPBearer`` dependency.

        Returns:
            List of scope strings parsed from the token's ``scopes`` claim,
            or an empty list when the claim is absent.
        """
        # Use the project's TokenManager to validate the Bearer token and
        # extract the scope claim.  CODEX_AUTH_SECRET must be set in the
        # environment (configured via the app's settings or a secrets manager).
        import os

        try:
            from codex.auth.token_manager import TokenManager
        except ImportError:
            logger.error("codex.auth.token_manager unavailable; cannot validate token")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable.",
            )

        secret = os.environ.get("CODEX_AUTH_SECRET", "")
        if not secret:
            logger.error("CODEX_AUTH_SECRET not set; refusing to validate token")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service misconfigured.",
            )

        token_mgr = TokenManager(secret_key=secret)
        bearer_token = credentials.credentials
        try:
            claims = token_mgr.validate_token(bearer_token)
        except ValueError as exc:
            msg = str(exc).lower()
            if "expired" in msg:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired.",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from exc
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        # scope is stored as a space-delimited string in the JWT claim.
        scope_str: str = claims.scope or ""
        return [s for s in scope_str.split() if s]

    async def scope_validator_dependency(
        scopes: list[str] = Depends(get_token_scopes),
    ) -> ScopeValidator:
        """FastAPI dependency to create and set scope validator.

        Use this as a dependency in routes that need scope checking:

        Example:
            >>> @app.get("/repo/{repo_id}")
            ... async def get_repo(
            ...     repo_id: str,
            ...     validator: ScopeValidator = Depends(scope_validator_dependency)
            ... ):
            ...     validator.require_scope(TokenScope.READ_REPO)
            ...     ...
        """
        validator = ScopeValidator(scopes)
        set_scope_validator(validator)
        return validator

except ImportError:
    # FastAPI not installed, skip dependency helpers
    logger.debug("Suppressed exception in handler", exc_info=True)


def scope_metadata(func: Callable) -> dict:
    """Extract scope metadata from decorated function.

    Args:
        func: Function to inspect

    Returns:
        Dictionary with scope metadata

    Example:
        >>> @require_scope("repo:write")
        ... def my_func():
        ...     pass
        >>> scope_metadata(my_func)
        {'protected': True, 'required': ['repo:write'], 'any': False}
    """
    return {
        "protected": getattr(func, "__scope_protected__", False),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }
