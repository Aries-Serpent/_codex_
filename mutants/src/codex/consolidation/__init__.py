"""
Consolidated utilities for duplication elimination.

This module provides centralized implementations of frequently-duplicated patterns
across the codebase, extracted during Phase 6 Wave 2 duplication consolidation campaign.

Pattern Groups:
  - Decorators: Validation, authorization, and error handling decorators
  - Errors: Centralized error handling and wrapping utilities
  - Test Fixtures: Shared pytest fixtures and factory utilities
  - Configuration: BaseConfig and ConfigParser utilities
  - Mocks: Mock/stub object factories for testing
  - Logging: Logger bootstrap and configuration utilities
  - Async Utils: Async context managers and retry logic

Modules:
  - decorators: @validate, @require_auth, @handle_errors decorators
  - errors: Error wrapping, exception handlers, error response builders
  - test_fixtures: Test fixture factories and utilities (MRC-001)
  - config: Configuration parsing and validation (MRC-002)
  - mocks: Mock/stub factories (MRC-003)
  - logging_bootstrap: Logger setup utilities (MRC-004)
  - async_utils: Async context managers (MRC-005)
"""

from codex.consolidation.async_utils import (
    AsyncContextBase,
    AsyncPoolManager,
    AsyncResourceManager,
    AsyncRetryManager,
    AsyncTimeout,
    async_managed_resource,
    async_pool_connection,
    async_timeout_context,
)
from codex.consolidation.config import (
    BaseConfig,
    ConfigParser,
    ConfigValidator,
    DefaultConfig,
)
from codex.consolidation.decorators import (
    handle_async_errors,
    handle_errors,
    require_auth,
    validate,
)
from codex.consolidation.errors import (
    AsyncErrorHandler,
    AuthenticationError,
    ErrorHandler,
    ErrorResponse,
    ErrorSeverity,
    create_error_response,
    wrap_async_with_error_handling,
    wrap_with_error_handling,
)
from codex.consolidation.logging_bootstrap import (
    ContextLogger,
    LogFormats,
    LoggerBootstrap,
    LoggingConfig,
    LogLevel,
)
from codex.consolidation.mocks import (
    AsyncFakeServiceFactory,
    AsyncMockClientFactory,
    FakeModel,
    FakeRepositoryFactory,
    FakeServiceFactory,
    MockClientFactory,
    ObjectFactory,
    StubDataFactory,
)

# Test fixtures are intentionally NOT imported here to avoid making pytest
# a runtime dependency of the core package. Import from:
#   from codex.consolidation.test_fixtures import FixtureFactory  # in test code only
# Note: This requires pytest to be installed separately (e.g., via `pip install codex-ml[full]`)
# or directly: `pip install pytest`

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
    # Configuration (MRC-002)
    "BaseConfig",
    "ConfigValidator",
    "ConfigParser",
    "DefaultConfig",
    # Mocks (MRC-003)
    "ObjectFactory",
    "FakeModel",
    "MockClientFactory",
    "AsyncMockClientFactory",
    "FakeRepositoryFactory",
    "FakeServiceFactory",
    "AsyncFakeServiceFactory",
    "StubDataFactory",
    # Logging (MRC-004)
    "LogLevel",
    "LogFormats",
    "LoggerBootstrap",
    "ContextLogger",
    "LoggingConfig",
    # Async utilities (MRC-005)
    "AsyncContextBase",
    "AsyncResourceManager",
    "AsyncPoolManager",
    "AsyncTimeout",
    "AsyncRetryManager",
    "async_managed_resource",
    "async_pool_connection",
    "async_timeout_context",
    # NOTE: Test fixtures (MRC-001) intentionally excluded to avoid pytest dependency
    # Import from test code: from codex.consolidation.test_fixtures import FixtureFactory
]
