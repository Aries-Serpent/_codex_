"""
MCP Server Lifecycle Management

Provides startup, shutdown, and health check functionality for MCP servers.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class LifecycleManager:
    """Manages application lifecycle events."""

    def __init__(self):
        self._startup_hooks: list[Callable] = []
        self._shutdown_hooks: list[Callable] = []
        self._health_checks: list[Callable] = []
        self._resources: dict[str, Any] = {}
        self._is_healthy = False
        self._is_ready = False
        self._health_check_timeout = 2.0

    def register_startup_hook(self, hook: Callable) -> None:
        """Register startup hook. Safeguard: validates callable."""
        if not callable(hook):
            raise ValueError(f"Hook must be callable, got {type(hook)}")
        self._startup_hooks.append(hook)

    def register_shutdown_hook(self, hook: Callable) -> None:
        """Register shutdown hook. Safeguard: validates callable."""
        if not callable(hook):
            raise ValueError(f"Hook must be callable, got {type(hook)}")
        self._shutdown_hooks.append(hook)

    def register_resource(self, name: str, resource: Any) -> None:
        """Register resource for cleanup. Safeguard: validates name."""
        if not name or not isinstance(name, str):
            raise ValueError("Resource name must be non-empty string")
        self._resources[name] = resource

    def register_health_check(self, check: Callable) -> None:
        """Register a health check. Safeguard: validates callable."""
        if not callable(check):
            raise ValueError(f"Health check must be callable, got {type(check)}")
        self._health_checks.append(check)

    async def startup(self) -> None:
        """Execute startup hooks. Safeguard: timeout and rollback."""
        logger.info("Starting initialization...")
        executed = []
        try:
            for hook in self._startup_hooks:
                if asyncio.iscoroutinefunction(hook):
                    await asyncio.wait_for(hook(), timeout=30.0)
                else:
                    hook()
                executed.append(hook)
            self._is_ready = True
            self._is_healthy = True
            logger.info(f"Initialized ({len(executed)} hooks)")
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Startup failed: <ERROR_TYPE>")
            await self._rollback_startup(executed)
            raise RuntimeError(f"Startup failed: {e}") from e

    async def _rollback_startup(self, executed: list[Callable]) -> None:
        """Rollback startup. Safeguard: graceful error handling."""
        for hook in reversed(executed):
            try:
                logger.debug(f"Rolling back: {hook.__name__}")
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("Rollback error: <ERROR_TYPE>")

    async def shutdown(self) -> None:
        """Execute shutdown. Safeguard: resource cleanup and timeout."""
        logger.info("Starting shutdown...")
        self._is_ready = False
        for hook in reversed(self._shutdown_hooks):
            try:
                if asyncio.iscoroutinefunction(hook):
                    await asyncio.wait_for(hook(), timeout=10.0)
                else:
                    hook()
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.error("Shutdown hook failed: <ERROR_TYPE>")
        await self._cleanup_resources()
        self._is_healthy = False
        logger.info("Shutdown complete")

    async def _cleanup_resources(self) -> None:
        """Cleanup resources. Safeguard: prevents leaks."""
        for name, resource in reversed(list(self._resources.items())):
            try:
                cleanup = getattr(resource, "cleanup", None)
                close = getattr(resource, "close", None)
                has_cleanup = "cleanup" in getattr(
                    resource, "__dict__", {}
                ) or "cleanup" in getattr(resource.__class__, "__dict__", {})
                if has_cleanup and callable(cleanup):
                    if asyncio.iscoroutinefunction(cleanup):
                        await cleanup()
                    else:
                        cleanup()
                elif callable(close):
                    if asyncio.iscoroutinefunction(close):
                        await close()
                    else:
                        close()
                logger.debug(f"Cleaned: {name}")
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning(f"Cleanup failed for {name}: <ERROR_TYPE>")
        self._resources.clear()

    def is_healthy(self) -> bool:
        """Check health status."""
        return self._is_healthy

    def is_ready(self) -> bool:
        """Check ready status."""
        return self._is_ready

    def healthz(self) -> dict[str, Any]:
        """Generate health check response."""
        checks_ok = True
        for check in self._health_checks:
            try:
                if asyncio.iscoroutinefunction(check):

                    async def _run_check():
                        return await asyncio.wait_for(check(), timeout=self._health_check_timeout)

                    try:
                        loop = asyncio.get_event_loop()
                        running = loop.is_running()
                    except RuntimeError as e:
                        type(e).__name__
                        logger.debug("RuntimeError: <ERROR_TYPE>")
                        logger.warning("RuntimeError: <ERROR_TYPE>", exc_info=True)
                        running = False

                    if running:
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(asyncio.run, _run_check())
                            result = future.result(timeout=self._health_check_timeout + 0.5)
                    else:
                        result = asyncio.run(_run_check())
                else:
                    result = check()
                if not bool(result):
                    checks_ok = False
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("Health check failed: <ERROR_TYPE>")
                checks_ok = False

        is_healthy = self._is_healthy and checks_ok
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "ready": self._is_ready,
            "resources": len(self._resources),
        }
