"""MCP lifecycle management for server state transitions.

This module provides server lifecycle management including:
- Server initialization and shutdown
- Health checks and readiness probes
- Graceful shutdown handling
- State transitions with validation
"""

import asyncio
import logging
import signal
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ServerState(Enum):
    """Server state enumeration."""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    DRAINING = "draining"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


# Valid state transitions
VALID_TRANSITIONS: dict[ServerState, list[ServerState]] = {
    ServerState.UNINITIALIZED: [ServerState.INITIALIZING],
    ServerState.INITIALIZING: [ServerState.READY, ServerState.ERROR],
    ServerState.READY: [ServerState.RUNNING, ServerState.STOPPING],
    ServerState.RUNNING: [
        ServerState.DRAINING,
        ServerState.STOPPING,
        ServerState.ERROR,
    ],
    ServerState.DRAINING: [ServerState.STOPPING],
    ServerState.STOPPING: [ServerState.STOPPED],
    ServerState.STOPPED: [ServerState.INITIALIZING],
    ServerState.ERROR: [ServerState.STOPPING, ServerState.INITIALIZING],
}


class InvalidStateTransition(Exception):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, current: ServerState, target: ServerState) -> None:
        """Initialize the exception.

        Args:
            current: Current server state.
            target: Target state that was attempted.
        """
        self.current = current
        self.target = target
        super().__init__(f"Invalid state transition from {current.value} to {target.value}")


@dataclass
class HealthStatus:
    """Health check result."""

    healthy: bool
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class LifecycleConfig:
    """Lifecycle configuration."""

    shutdown_timeout_seconds: float = 30.0
    health_check_interval_seconds: float = 10.0
    drain_timeout_seconds: float = 60.0
    max_concurrent_requests: int = 100


class LifecycleManager:
    """Manages MCP server lifecycle."""

    def __init__(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.

        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)

    @property
    def state(self) -> ServerState:
        """Get current server state."""
        return self._state

    @property
    def is_healthy(self) -> bool:
        """Check if server is in a healthy state."""
        return self._state in (ServerState.READY, ServerState.RUNNING)

    @property
    def is_accepting_requests(self) -> bool:
        """Check if server is accepting new requests."""
        return self._state == ServerState.RUNNING

    async def transition_to(self, target: ServerState) -> None:
        """Transition to a new state with validation.

        Args:
            target: Target state to transition to.

        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)

            old_state = self._state
            self._state = target
            self._logger.info("State transition: %s -> %s", old_state.value, target.value)

    def register_health_check(self, check: Callable[[], HealthStatus]) -> None:
        """Register a health check function.

        Args:
            check: Health check function that returns HealthStatus.
        """
        self._health_checks.append(check)

    def register_startup_hook(self, hook: Callable[[], None]) -> None:
        """Register a startup hook.

        Args:
            hook: Function to call during startup.
        """
        self._startup_hooks.append(hook)

    def register_shutdown_hook(self, hook: Callable[[], None]) -> None:
        """Register a shutdown hook.

        Args:
            hook: Function to call during shutdown.
        """
        self._shutdown_hooks.append(hook)

    async def initialize(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)

        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()

            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")

        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            self._logger.error("Initialization failed: %s", e)
            await self.transition_to(ServerState.ERROR)
            raise

    async def start(self) -> None:
        """Start accepting requests."""
        if self._state != ServerState.READY:
            raise InvalidStateTransition(self._state, ServerState.RUNNING)

        await self.transition_to(ServerState.RUNNING)
        self._logger.info("Server started and accepting requests")

    async def shutdown(self, graceful: bool = True) -> None:
        """Shutdown the server.

        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)

            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests,
                    )
                    break
                await asyncio.sleep(0.1)

        await self.transition_to(ServerState.STOPPING)

        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                self._logger.error("Shutdown hook failed: %s", e)

        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")

    async def track_request_start(self) -> bool:
        """Track the start of a request.

        Returns:
            True if the request can proceed, False if server is draining.
        """
        if not self.is_accepting_requests:
            return False

        async with self._requests_lock:
            if self._active_requests >= self._config.max_concurrent_requests:
                return False
            self._active_requests += 1
        return True

    async def track_request_end(self) -> None:
        """Track the end of a request."""
        async with self._requests_lock:
            self._active_requests = max(0, self._active_requests - 1)

    def get_health(self) -> HealthStatus:
        """Get aggregated health status.

        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value},
            )

        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []

        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message,
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")

        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details,
        )

    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown to complete."""
        await self._shutdown_event.wait()

    def setup_signal_handlers(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()

        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(graceful=True)),  # type: ignore[misc]
            )

        self._logger.info("Signal handlers configured")


# Module-level instance for convenience
_lifecycle_manager: Optional[LifecycleManager] = None


def get_lifecycle_manager() -> LifecycleManager:
    """Get or create the global lifecycle manager.

    Returns:
        The global LifecycleManager instance.
    """
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = LifecycleManager()
    return _lifecycle_manager


def reset_lifecycle_manager() -> None:
    """Reset the global lifecycle manager (for testing)."""
    global _lifecycle_manager
    _lifecycle_manager = None
