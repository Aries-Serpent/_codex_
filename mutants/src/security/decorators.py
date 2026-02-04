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
)

logger = logging.getLogger(__name__)

# Context variable for storing current request's scope validator
_scope_validator_context: ContextVar[Optional[ScopeValidator]] = ContextVar(
    "scope_validator", default=None
)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_set_scope_validator__mutmut_orig(validator: ScopeValidator) -> None:
    """Set scope validator for current request context.
    
    This should be called by middleware/dependency injection
    after extracting token scopes from the request.
    
    Args:
        validator: ScopeValidator instance for current request
    """
    _scope_validator_context.set(validator)


def x_set_scope_validator__mutmut_1(validator: ScopeValidator) -> None:
    """Set scope validator for current request context.
    
    This should be called by middleware/dependency injection
    after extracting token scopes from the request.
    
    Args:
        validator: ScopeValidator instance for current request
    """
    _scope_validator_context.set(None)

x_set_scope_validator__mutmut_mutants : ClassVar[MutantDict] = {
'x_set_scope_validator__mutmut_1': x_set_scope_validator__mutmut_1
}

def set_scope_validator(*args, **kwargs):
    result = _mutmut_trampoline(x_set_scope_validator__mutmut_orig, x_set_scope_validator__mutmut_mutants, args, kwargs)
    return result 

set_scope_validator.__signature__ = _mutmut_signature(x_set_scope_validator__mutmut_orig)
x_set_scope_validator__mutmut_orig.__name__ = 'x_set_scope_validator'


def get_scope_validator() -> Optional[ScopeValidator]:
    """Get scope validator from current request context.
    
    Returns:
        ScopeValidator instance or None if not set
    """
    return _scope_validator_context.get()


def clear_scope_validator() -> None:
    """Clear scope validator from current request context."""
    _scope_validator_context.set(None)


def x_require_scope__mutmut_orig(*required_scopes: str) -> Callable:
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


def x_require_scope__mutmut_1(*required_scopes: str) -> Callable:
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
    required_scope_flags = None
    
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


def x_require_scope__mutmut_2(*required_scopes: str) -> Callable:
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
    required_scope_flags = TokenScope.from_list(None)
    
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


def x_require_scope__mutmut_3(*required_scopes: str) -> Callable:
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
    required_scope_flags = TokenScope.from_list(list(None))
    
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


def x_require_scope__mutmut_4(*required_scopes: str) -> Callable:
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
        wrapper.__required_scopes__ = None  # type: ignore
        wrapper.__scope_protected__ = True  # type: ignore
        
        return wrapper
    
    return decorator


def x_require_scope__mutmut_5(*required_scopes: str) -> Callable:
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
        wrapper.__scope_protected__ = None  # type: ignore
        
        return wrapper
    
    return decorator


def x_require_scope__mutmut_6(*required_scopes: str) -> Callable:
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
        wrapper.__scope_protected__ = False  # type: ignore
        
        return wrapper
    
    return decorator

x_require_scope__mutmut_mutants : ClassVar[MutantDict] = {
'x_require_scope__mutmut_1': x_require_scope__mutmut_1, 
    'x_require_scope__mutmut_2': x_require_scope__mutmut_2, 
    'x_require_scope__mutmut_3': x_require_scope__mutmut_3, 
    'x_require_scope__mutmut_4': x_require_scope__mutmut_4, 
    'x_require_scope__mutmut_5': x_require_scope__mutmut_5, 
    'x_require_scope__mutmut_6': x_require_scope__mutmut_6
}

def require_scope(*args, **kwargs):
    result = _mutmut_trampoline(x_require_scope__mutmut_orig, x_require_scope__mutmut_mutants, args, kwargs)
    return result 

require_scope.__signature__ = _mutmut_signature(x_require_scope__mutmut_orig)
x_require_scope__mutmut_orig.__name__ = 'x_require_scope'


def x_require_any_scope__mutmut_orig(*required_scopes: str) -> Callable:
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


def x_require_any_scope__mutmut_1(*required_scopes: str) -> Callable:
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
    required_scope_flags = None
    
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


def x_require_any_scope__mutmut_2(*required_scopes: str) -> Callable:
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
        TokenScope.from_string(None) for scope in required_scopes
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


def x_require_any_scope__mutmut_3(*required_scopes: str) -> Callable:
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
        wrapper.__required_scopes__ = None  # type: ignore
        wrapper.__scope_protected__ = True  # type: ignore
        wrapper.__scope_any__ = True  # type: ignore
        
        return wrapper
    
    return decorator


def x_require_any_scope__mutmut_4(*required_scopes: str) -> Callable:
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
        wrapper.__scope_protected__ = None  # type: ignore
        wrapper.__scope_any__ = True  # type: ignore
        
        return wrapper
    
    return decorator


def x_require_any_scope__mutmut_5(*required_scopes: str) -> Callable:
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
        wrapper.__scope_protected__ = False  # type: ignore
        wrapper.__scope_any__ = True  # type: ignore
        
        return wrapper
    
    return decorator


def x_require_any_scope__mutmut_6(*required_scopes: str) -> Callable:
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
        wrapper.__scope_any__ = None  # type: ignore
        
        return wrapper
    
    return decorator


def x_require_any_scope__mutmut_7(*required_scopes: str) -> Callable:
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
        wrapper.__scope_any__ = False  # type: ignore
        
        return wrapper
    
    return decorator

x_require_any_scope__mutmut_mutants : ClassVar[MutantDict] = {
'x_require_any_scope__mutmut_1': x_require_any_scope__mutmut_1, 
    'x_require_any_scope__mutmut_2': x_require_any_scope__mutmut_2, 
    'x_require_any_scope__mutmut_3': x_require_any_scope__mutmut_3, 
    'x_require_any_scope__mutmut_4': x_require_any_scope__mutmut_4, 
    'x_require_any_scope__mutmut_5': x_require_any_scope__mutmut_5, 
    'x_require_any_scope__mutmut_6': x_require_any_scope__mutmut_6, 
    'x_require_any_scope__mutmut_7': x_require_any_scope__mutmut_7
}

def require_any_scope(*args, **kwargs):
    result = _mutmut_trampoline(x_require_any_scope__mutmut_orig, x_require_any_scope__mutmut_mutants, args, kwargs)
    return result 

require_any_scope.__signature__ = _mutmut_signature(x_require_any_scope__mutmut_orig)
x_require_any_scope__mutmut_orig.__name__ = 'x_require_any_scope'


def x_optional_scope__mutmut_orig(*scopes: str) -> Callable:
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


def x_optional_scope__mutmut_1(*scopes: str) -> Callable:
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
        wrapper.__optional_scopes__ = None  # type: ignore
        wrapper.__scope_optional__ = True  # type: ignore
        
        return wrapper
    
    return decorator


def x_optional_scope__mutmut_2(*scopes: str) -> Callable:
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
        wrapper.__scope_optional__ = None  # type: ignore
        
        return wrapper
    
    return decorator


def x_optional_scope__mutmut_3(*scopes: str) -> Callable:
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
        wrapper.__scope_optional__ = False  # type: ignore
        
        return wrapper
    
    return decorator

x_optional_scope__mutmut_mutants : ClassVar[MutantDict] = {
'x_optional_scope__mutmut_1': x_optional_scope__mutmut_1, 
    'x_optional_scope__mutmut_2': x_optional_scope__mutmut_2, 
    'x_optional_scope__mutmut_3': x_optional_scope__mutmut_3
}

def optional_scope(*args, **kwargs):
    result = _mutmut_trampoline(x_optional_scope__mutmut_orig, x_optional_scope__mutmut_mutants, args, kwargs)
    return result 

optional_scope.__signature__ = _mutmut_signature(x_optional_scope__mutmut_orig)
x_optional_scope__mutmut_orig.__name__ = 'x_optional_scope'


# FastAPI dependency injection helpers
try:
    from fastapi import Depends, HTTPException, status  # noqa: F401 - Optional FastAPI integration
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # noqa: F401
    
    security = HTTPBearer()
    
    async def get_token_scopes(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> List[str]:
        """FastAPI dependency to extract scopes from token.
        
        **CRITICAL SECURITY WARNING**: This placeholder implementation MUST be
        replaced with actual token validation before production deployment.
        
        The current implementation raises NotImplementedError to ensure fail-closed
        behavior and prevent unintended access grants.
        
        Production implementations should:
        1. Validate the token signature and expiration
        2. Extract scopes/permissions from token payload
        3. Return the actual scopes for authorization checks
        
        Implementation Examples:
        
        **Option 1: JWT Token Validation (Recommended for stateless auth)**
        
        ```python
        import jwt
        from fastapi import Depends, HTTPException, status
        from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
        
        async def get_token_scopes(
            credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        ) -> List[str]:
            try:
                token = credentials.credentials
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET_KEY,
                    algorithms=[settings.JWT_ALGORITHM],
                    audience=settings.JWT_AUDIENCE,
                )
                return payload.get("scopes", [])
            except jwt.ExpiredSignatureError:
                raise HTTPException(401, "Token expired")
            except jwt.InvalidTokenError:
                raise HTTPException(401, "Invalid token")
        ```
        
        Configuration: JWT_SECRET_KEY, JWT_ALGORITHM (e.g., "HS256"), JWT_AUDIENCE
        
        **Option 2: OAuth Token Introspection (RFC 7662)**
        
        ```python
        import httpx
        from fastapi import Depends, HTTPException
        
        async def get_token_scopes(
            credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        ) -> List[str]:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.OAUTH_INTROSPECTION_ENDPOINT,
                    data={"token": credentials.credentials},
                    auth=(settings.OAUTH_CLIENT_ID, settings.OAUTH_CLIENT_SECRET),
                )
                data = response.json()
                if not data.get("active"):
                    raise HTTPException(401, "Token not active")
                return data.get("scope", "").split()
        ```
        
        Configuration: OAUTH_INTROSPECTION_ENDPOINT, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET
        
        **Testing with Mocks:**
        
        ```python
        from unittest.mock import AsyncMock
        
        @pytest.mark.asyncio
        async def test_endpoint(mocker):
            mocker.patch("module.get_token_scopes", 
                        new=AsyncMock(return_value=["read:data"]))
            # Test protected endpoint...
        ```
        
        Args:
            credentials: Bearer token from request
            
        Returns:
            List of scope strings (never reached - raises error)
            
        Raises:
            NotImplementedError: Always raised to prevent production use
        """
        # This placeholder must not be used in production as it would
        # grant unintended access. Raise an error instead of returning
        # hardcoded scopes to ensure a fail-closed behavior.
        logger.error(
            "Token scope extraction is not implemented. "
            "Replace get_token_scopes with a real implementation before production."
        )
        raise NotImplementedError(
            "Token scope extraction is not implemented. "
            "Implement get_token_scopes to validate tokens and extract scopes."
        )
    
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


def x_scope_metadata__mutmut_orig(func: Callable) -> dict:
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


def x_scope_metadata__mutmut_1(func: Callable) -> dict:
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
        "XXprotectedXX": getattr(func, "__scope_protected__", False),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_2(func: Callable) -> dict:
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
        "PROTECTED": getattr(func, "__scope_protected__", False),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_3(func: Callable) -> dict:
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
        "protected": getattr(None, "__scope_protected__", False),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_4(func: Callable) -> dict:
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
        "protected": getattr(func, None, False),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_5(func: Callable) -> dict:
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
        "protected": getattr(func, "__scope_protected__", None),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_6(func: Callable) -> dict:
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
        "protected": getattr("__scope_protected__", False),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_7(func: Callable) -> dict:
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
        "protected": getattr(func, False),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_8(func: Callable) -> dict:
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
        "protected": getattr(func, "__scope_protected__", ),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_9(func: Callable) -> dict:
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
        "protected": getattr(func, "XX__scope_protected__XX", False),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_10(func: Callable) -> dict:
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
        "protected": getattr(func, "__SCOPE_PROTECTED__", False),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_11(func: Callable) -> dict:
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
        "protected": getattr(func, "__scope_protected__", True),
        "optional": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_12(func: Callable) -> dict:
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
        "XXoptionalXX": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_13(func: Callable) -> dict:
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
        "OPTIONAL": getattr(func, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_14(func: Callable) -> dict:
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
        "optional": getattr(None, "__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_15(func: Callable) -> dict:
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
        "optional": getattr(func, None, False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_16(func: Callable) -> dict:
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
        "optional": getattr(func, "__scope_optional__", None),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_17(func: Callable) -> dict:
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
        "optional": getattr("__scope_optional__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_18(func: Callable) -> dict:
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
        "optional": getattr(func, False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_19(func: Callable) -> dict:
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
        "optional": getattr(func, "__scope_optional__", ),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_20(func: Callable) -> dict:
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
        "optional": getattr(func, "XX__scope_optional__XX", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_21(func: Callable) -> dict:
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
        "optional": getattr(func, "__SCOPE_OPTIONAL__", False),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_22(func: Callable) -> dict:
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
        "optional": getattr(func, "__scope_optional__", True),
        "required": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_23(func: Callable) -> dict:
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
        "XXrequiredXX": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_24(func: Callable) -> dict:
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
        "REQUIRED": getattr(func, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_25(func: Callable) -> dict:
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
        "required": getattr(None, "__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_26(func: Callable) -> dict:
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
        "required": getattr(func, None, []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_27(func: Callable) -> dict:
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
        "required": getattr(func, "__required_scopes__", None),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_28(func: Callable) -> dict:
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
        "required": getattr("__required_scopes__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_29(func: Callable) -> dict:
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
        "required": getattr(func, []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_30(func: Callable) -> dict:
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
        "required": getattr(func, "__required_scopes__", ),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_31(func: Callable) -> dict:
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
        "required": getattr(func, "XX__required_scopes__XX", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_32(func: Callable) -> dict:
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
        "required": getattr(func, "__REQUIRED_SCOPES__", []),
        "any": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_33(func: Callable) -> dict:
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
        "XXanyXX": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_34(func: Callable) -> dict:
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
        "ANY": getattr(func, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_35(func: Callable) -> dict:
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
        "any": getattr(None, "__scope_any__", False),
    }


def x_scope_metadata__mutmut_36(func: Callable) -> dict:
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
        "any": getattr(func, None, False),
    }


def x_scope_metadata__mutmut_37(func: Callable) -> dict:
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
        "any": getattr(func, "__scope_any__", None),
    }


def x_scope_metadata__mutmut_38(func: Callable) -> dict:
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
        "any": getattr("__scope_any__", False),
    }


def x_scope_metadata__mutmut_39(func: Callable) -> dict:
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
        "any": getattr(func, False),
    }


def x_scope_metadata__mutmut_40(func: Callable) -> dict:
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
        "any": getattr(func, "__scope_any__", ),
    }


def x_scope_metadata__mutmut_41(func: Callable) -> dict:
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
        "any": getattr(func, "XX__scope_any__XX", False),
    }


def x_scope_metadata__mutmut_42(func: Callable) -> dict:
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
        "any": getattr(func, "__SCOPE_ANY__", False),
    }


def x_scope_metadata__mutmut_43(func: Callable) -> dict:
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
        "any": getattr(func, "__scope_any__", True),
    }

x_scope_metadata__mutmut_mutants : ClassVar[MutantDict] = {
'x_scope_metadata__mutmut_1': x_scope_metadata__mutmut_1, 
    'x_scope_metadata__mutmut_2': x_scope_metadata__mutmut_2, 
    'x_scope_metadata__mutmut_3': x_scope_metadata__mutmut_3, 
    'x_scope_metadata__mutmut_4': x_scope_metadata__mutmut_4, 
    'x_scope_metadata__mutmut_5': x_scope_metadata__mutmut_5, 
    'x_scope_metadata__mutmut_6': x_scope_metadata__mutmut_6, 
    'x_scope_metadata__mutmut_7': x_scope_metadata__mutmut_7, 
    'x_scope_metadata__mutmut_8': x_scope_metadata__mutmut_8, 
    'x_scope_metadata__mutmut_9': x_scope_metadata__mutmut_9, 
    'x_scope_metadata__mutmut_10': x_scope_metadata__mutmut_10, 
    'x_scope_metadata__mutmut_11': x_scope_metadata__mutmut_11, 
    'x_scope_metadata__mutmut_12': x_scope_metadata__mutmut_12, 
    'x_scope_metadata__mutmut_13': x_scope_metadata__mutmut_13, 
    'x_scope_metadata__mutmut_14': x_scope_metadata__mutmut_14, 
    'x_scope_metadata__mutmut_15': x_scope_metadata__mutmut_15, 
    'x_scope_metadata__mutmut_16': x_scope_metadata__mutmut_16, 
    'x_scope_metadata__mutmut_17': x_scope_metadata__mutmut_17, 
    'x_scope_metadata__mutmut_18': x_scope_metadata__mutmut_18, 
    'x_scope_metadata__mutmut_19': x_scope_metadata__mutmut_19, 
    'x_scope_metadata__mutmut_20': x_scope_metadata__mutmut_20, 
    'x_scope_metadata__mutmut_21': x_scope_metadata__mutmut_21, 
    'x_scope_metadata__mutmut_22': x_scope_metadata__mutmut_22, 
    'x_scope_metadata__mutmut_23': x_scope_metadata__mutmut_23, 
    'x_scope_metadata__mutmut_24': x_scope_metadata__mutmut_24, 
    'x_scope_metadata__mutmut_25': x_scope_metadata__mutmut_25, 
    'x_scope_metadata__mutmut_26': x_scope_metadata__mutmut_26, 
    'x_scope_metadata__mutmut_27': x_scope_metadata__mutmut_27, 
    'x_scope_metadata__mutmut_28': x_scope_metadata__mutmut_28, 
    'x_scope_metadata__mutmut_29': x_scope_metadata__mutmut_29, 
    'x_scope_metadata__mutmut_30': x_scope_metadata__mutmut_30, 
    'x_scope_metadata__mutmut_31': x_scope_metadata__mutmut_31, 
    'x_scope_metadata__mutmut_32': x_scope_metadata__mutmut_32, 
    'x_scope_metadata__mutmut_33': x_scope_metadata__mutmut_33, 
    'x_scope_metadata__mutmut_34': x_scope_metadata__mutmut_34, 
    'x_scope_metadata__mutmut_35': x_scope_metadata__mutmut_35, 
    'x_scope_metadata__mutmut_36': x_scope_metadata__mutmut_36, 
    'x_scope_metadata__mutmut_37': x_scope_metadata__mutmut_37, 
    'x_scope_metadata__mutmut_38': x_scope_metadata__mutmut_38, 
    'x_scope_metadata__mutmut_39': x_scope_metadata__mutmut_39, 
    'x_scope_metadata__mutmut_40': x_scope_metadata__mutmut_40, 
    'x_scope_metadata__mutmut_41': x_scope_metadata__mutmut_41, 
    'x_scope_metadata__mutmut_42': x_scope_metadata__mutmut_42, 
    'x_scope_metadata__mutmut_43': x_scope_metadata__mutmut_43
}

def scope_metadata(*args, **kwargs):
    result = _mutmut_trampoline(x_scope_metadata__mutmut_orig, x_scope_metadata__mutmut_mutants, args, kwargs)
    return result 

scope_metadata.__signature__ = _mutmut_signature(x_scope_metadata__mutmut_orig)
x_scope_metadata__mutmut_orig.__name__ = 'x_scope_metadata'
