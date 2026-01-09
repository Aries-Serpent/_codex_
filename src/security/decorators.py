"""Security decorators for scope-based authorization.

This module provides decorators for enforcing scope requirements
in API endpoints and service methods.

Part of PS-05 Enhancement: Scope Validation Library - Priority 4
"""

from __future__ import annotations

import functools
import logging
from typing import Callable, List, Optional, Any
from contextvars import ContextVar

from security.scope_validator import (
    TokenScope,
    ScopeValidator,
    InsufficientScopeError,
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
            
            logger.debug(
                f"Scope check passed for {func.__name__}: {required_scopes}"
            )
            
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
    required_scope_flags = [
        TokenScope.from_string(scope) for scope in required_scopes
    ]
    
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
            
            logger.debug(
                f"Scope check passed for {func.__name__}: one of {required_scopes}"
            )
            
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
                logger.debug(
                    f"Optional scope check for {func.__name__}: "
                    f"{scopes} = {has_scopes}"
                )
            
            # Execute function regardless
            return func(*args, **kwargs)
        
        # Store metadata
        wrapper.__optional_scopes__ = scopes  # type: ignore
        wrapper.__scope_optional__ = True  # type: ignore
        
        return wrapper
    
    return decorator


# FastAPI dependency injection helpers
try:
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    
    security = HTTPBearer()
    
    async def get_token_scopes(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> List[str]:
        """FastAPI dependency to extract scopes from token.
        
        This is a placeholder that should be customized to decode
        your actual tokens (JWT, OAuth, etc.) and extract scopes.
        
        Args:
            credentials: Bearer token from request
            
        Returns:
            List of scope strings
            
        Raises:
            HTTPException: If token is invalid
        """
        _token = credentials.credentials
        
        # TODO: Decode token and extract scopes
        # For JWT: jwt.decode(_token, ...) and read 'scope' claim
        # For OAuth: introspection endpoint
        
        # Placeholder implementation
        logger.warning("Using placeholder token scope extraction")
        return ["repo:read"]  # Default read-only
    
    async def scope_validator_dependency(
        scopes: List[str] = Depends(get_token_scopes),
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
    pass


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
