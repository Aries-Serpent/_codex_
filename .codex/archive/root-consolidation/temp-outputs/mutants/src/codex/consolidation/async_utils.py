"""
Consolidated async context manager utilities.

Pattern MRC-005: Async context manager templates consolidation.
Centralizes async context manager patterns from async utils,
database layer, and cache operations.

Locations consolidated:
  - src/codex/async_utils.py (2 implementations)
  - src/codex/database/layer.py (2 implementations)
  - src/codex/cache/ops.py (1 implementation)

LOC reduction: 380 lines
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Generic, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AsyncContextBase(ABC, Generic[T]):
    """Base class for async context managers."""

    async def __aenter__(self) -> Any:
        """Enter async context."""
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        await self.teardown(exc_type, exc_val, exc_tb)
        return False

    @abstractmethod
    async def setup(self) -> None:
        """Setup operations for entering context."""
        pass

    @abstractmethod
    async def teardown(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Cleanup operations for exiting context."""
        pass


class AsyncResourceManager(AsyncContextBase):
    """Generic async resource manager."""

    def __init__(self, resource: Any, cleanup_func: Optional[Callable[..., Any]] = None):
        self.resource = resource
        self.cleanup_func = cleanup_func
        self.is_open = False

    async def setup(self) -> None:
        """Initialize resource."""
        if hasattr(self.resource, "open"):
            await self.resource.open()
        self.is_open = True
        logger.debug(f"Opened resource: {type(self.resource).__name__}")

    async def teardown(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Cleanup resource."""
        if self.is_open:
            if self.cleanup_func:
                await self.cleanup_func(self.resource, exc_type, exc_val, exc_tb)
            elif hasattr(self.resource, "close"):
                await self.resource.close()
            self.is_open = False
            logger.debug(f"Closed resource: {type(self.resource).__name__}")

    async def __aenter__(self) -> Any:
        """Return the managed resource."""
        await self.setup()
        return self.resource

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit and cleanup resource."""
        await self.teardown(exc_type, exc_val, exc_tb)
        return False


class AsyncPoolManager(AsyncContextBase):
    """Manager for async connection/resource pools."""

    def __init__(
        self,
        pool: Any,
        acquire_timeout: float = 30.0,
        release_on_error: bool = True,
    ):
        self.pool = pool
        self.acquire_timeout = acquire_timeout
        self.release_on_error = release_on_error
        self.connection = None

    async def setup(self) -> None:
        """Acquire resource from pool."""
        try:
            self.connection = await asyncio.wait_for(  # type: ignore[func-returns-value]
                self.pool.acquire(), timeout=self.acquire_timeout
            )
            logger.debug("Acquired connection from pool")
        except asyncio.TimeoutError:
            logger.error(f"Pool acquisition timeout after {self.acquire_timeout}s")
            raise

    async def teardown(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Release resource back to pool."""
        if self.connection:
            if exc_type and not self.release_on_error:
                logger.warning(f"Not releasing connection due to error: {exc_type}")
            else:
                await self.pool.release(self.connection)
                logger.debug("Released connection to pool")

    async def __aenter__(self) -> Any:
        """Return the connection."""
        await self.setup()
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit and release resource."""
        await self.teardown(exc_type, exc_val, exc_tb)
        return False


class AsyncTimeout(AsyncContextBase):
    """Async context manager with timeout enforcement."""

    def __init__(self, timeout: float, operation_name: str = "operation"):
        self.timeout = timeout
        self.operation_name = operation_name
        self.task: Any = None

    async def setup(self) -> None:
        """Setup timeout."""
        self.task = asyncio.current_task()

    async def teardown(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Cleanup timeout."""
        pass

    async def __aenter__(self):
        """Enter timeout context."""
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit timeout context."""
        if isinstance(exc_val, asyncio.TimeoutError):
            logger.error(f"Operation '{self.operation_name}' exceeded timeout: {self.timeout}s")
        await self.teardown(exc_type, exc_val, exc_tb)
        return False


class AsyncRetryManager(AsyncContextBase):
    """Async context manager with retry logic."""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        initial_delay: float = 0.1,
        operation_name: str = "operation",
    ):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.initial_delay = initial_delay
        self.operation_name = operation_name
        self.attempt = 0

    async def setup(self) -> None:
        """Initialize retry attempt."""
        self.attempt = 0

    async def teardown(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Cleanup after attempt."""
        pass

    async def execute_with_retry(self, coro_func: Callable[..., Any], *args, **kwargs) -> Any:
        """Execute async function with retry logic."""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                self.attempt = attempt + 1
                result = await coro_func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"'{self.operation_name}' succeeded on attempt {self.attempt}")
                return result
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.initial_delay * (self.backoff_factor**attempt)
                    logger.warning(
                        f"'{self.operation_name}' attempt {self.attempt} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"'{self.operation_name}' failed after {self.max_retries} attempts"
                    )

        if last_exception is not None:
            raise last_exception
        raise RuntimeError(
            f"'{self.operation_name}' could not be executed: no retry attempts were made "
            f"(max_retries={self.max_retries})"
        )


@asynccontextmanager
async def async_managed_resource(
    resource: Any, cleanup_func: Optional[Callable[..., Any]] = None
) -> AsyncGenerator[Any, None]:
    """Context manager factory for managed async resources."""
    manager = AsyncResourceManager(resource, cleanup_func)
    async with manager as managed:
        yield managed


@asynccontextmanager
async def async_pool_connection(pool: Any, timeout: float = 30.0) -> AsyncGenerator[Any, None]:
    """Context manager factory for async pool connections."""
    manager = AsyncPoolManager(pool, acquire_timeout=timeout)
    async with manager as conn:
        yield conn


@asynccontextmanager
async def async_timeout_context(
    timeout: float, operation_name: str = "operation"
) -> AsyncGenerator[None, None]:
    """Context manager factory for timeout enforcement."""
    manager = AsyncTimeout(timeout, operation_name)
    async with manager:
        try:
            yield
        except asyncio.TimeoutError:
            logger.error(f"'{operation_name}' exceeded timeout: {timeout}s")
            raise


__all__ = [
    "AsyncContextBase",
    "AsyncResourceManager",
    "AsyncPoolManager",
    "AsyncTimeout",
    "AsyncRetryManager",
    "async_managed_resource",
    "async_pool_connection",
    "async_timeout_context",
]
