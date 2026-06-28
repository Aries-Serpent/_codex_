"""
Consolidated utilities for duplication elimination.

This module provides centralized implementations of frequently-duplicated patterns
across the codebase, extracted during Phase 6 Wave 2 duplication consolidation campaign.

Pattern Groups:
  - Decorators: Validation, authorization, and error handling decorators
  - Errors: Centralized error handling and wrapping utilities

Modules:
  - decorators: @validate, @require_auth, @handle_errors decorators
  - errors: Error wrapping, exception handlers, error response builders
"""

from src.codex.consolidation.decorators import (
    validate,
    require_auth,
    handle_errors,
    handle_async_errors,
)
from src.codex.consolidation.errors import (
    ErrorHandler,
    AsyncErrorHandler,
    ErrorResponse,
    ErrorSeverity,
    create_error_response,
    wrap_with_error_handling,
    wrap_async_with_error_handling,
    AuthenticationError,
)

__all__ = [
    # Decorators (LRC-002)
    "validate",
    "require_auth",
    "handle_errors",
    "handle_async_errors",
    # Error utilities (LRC-003)
    "ErrorHandler",
    "AsyncErrorHandler",
    "ErrorResponse",
    "ErrorSeverity",
    "create_error_response",
    "wrap_with_error_handling",
    "wrap_async_with_error_handling",
    "AuthenticationError",
]
