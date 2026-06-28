"""
Tenant-aware logging and tracing utilities for MSP Gateway.

This module provides decorators and context managers for propagating tenant
information through logging and distributed tracing.
"""

from __future__ import annotations

import contextvars
import functools
import logging
from typing import Any, Callable, Optional, TypeVar

from fastapi import Request

logger = logging.getLogger(__name__)

# Context variable for storing tenant_id across async boundaries
_tenant_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "tenant_id", default=None
)


def get_current_tenant_id() -> Optional[str]:
    """Get the current tenant ID from context.
    
    Returns:
        The current tenant ID, or None if not set.
    """
    return _tenant_context.get()


def set_tenant_context(tenant_id: str) -> None:
    """Set the current tenant ID in context.
    
    Args:
        tenant_id: The tenant identifier to set.
    """
    _tenant_context.set(tenant_id)


def clear_tenant_context() -> None:
    """Clear the current tenant ID from context."""
    _tenant_context.set(None)


class TenantContextManager:
    """Context manager for temporarily setting tenant context.
    
    Usage:
        with TenantContextManager("tenant-123"):
            # tenant_id is "tenant-123" here
            pass
    """

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.token: Optional[contextvars.Token[Optional[str]]] = None

    def __enter__(self):
        self.token = _tenant_context.set(self.tenant_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            _tenant_context.reset(self.token)
        return False


def tenant_logged(func: Callable) -> Callable:
    """Decorator to log function calls with tenant context.
    
    Usage:
        @tenant_logged
        async def my_function(request: Request):
            pass
    """

    @functools.wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        tenant = getattr(request.state, "tenant", None)
        tenant_id = tenant["tenant_id"] if tenant else None

        if tenant_id:
            set_tenant_context(tenant_id)
            logger.debug(
                "Executing %s for tenant %s",
                func.__name__,
                tenant_id,
            )

        try:
            result = await func(request, *args, **kwargs)
            if tenant_id:
                logger.debug("Completed %s for tenant %s", func.__name__, tenant_id)
            return result
        finally:
            clear_tenant_context()

    return wrapper


def extract_tenant_id_from_request(request: Request) -> Optional[str]:
    """Extract tenant ID from request state.
    
    Args:
        request: The FastAPI request object.
    
    Returns:
        The tenant ID if available, None otherwise.
    """
    tenant = getattr(request.state, "tenant", None)
    return tenant["tenant_id"] if tenant else None


class TenantAwareLogger:
    """Logger that automatically includes tenant ID in log records.
    
    Usage:
        logger = TenantAwareLogger(__name__)
        logger.info("Processing request", tenant_id="tenant-123")
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _get_tenant_context(self) -> dict[str, Any]:
        """Get tenant context for logging."""
        tenant_id = get_current_tenant_id()
        return {"tenant_id": tenant_id} if tenant_id else {}

    def info(self, msg: str, *args, **kwargs):
        """Log info level message with tenant context."""
        context = self._get_tenant_context()
        context.update(kwargs)
        self.logger.info(f"{msg} {context}", *args)

    def debug(self, msg: str, *args, **kwargs):
        """Log debug level message with tenant context."""
        context = self._get_tenant_context()
        context.update(kwargs)
        self.logger.debug(f"{msg} {context}", *args)

    def warning(self, msg: str, *args, **kwargs):
        """Log warning level message with tenant context."""
        context = self._get_tenant_context()
        context.update(kwargs)
        self.logger.warning(f"{msg} {context}", *args)

    def error(self, msg: str, *args, **kwargs):
        """Log error level message with tenant context."""
        context = self._get_tenant_context()
        context.update(kwargs)
        self.logger.error(f"{msg} {context}", *args)


__all__ = [
    "get_current_tenant_id",
    "set_tenant_context",
    "clear_tenant_context",
    "TenantContextManager",
    "tenant_logged",
    "extract_tenant_id_from_request",
    "TenantAwareLogger",
]
