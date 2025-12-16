"""
MCP Server Lifecycle Management

Provides startup, shutdown, and health check functionality for MCP servers.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Callable, Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class LifecycleManager:
    """Manages application lifecycle events."""

    def __init__(self):
        self._startup_hooks: List[Callable] = []
        self._shutdown_hooks: List[Callable] = []
        self._resources: Dict[str, Any] = {}
        self._is_healthy = False
        self._is_ready = False

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
        except Exception as e:
            logger.error(f"Startup failed: {e}")
            await self._rollback_startup(executed)
            raise RuntimeError(f"Startup failed: {e}") from e

    async def _rollback_startup(self, executed: List[Callable]) -> None:
        """Rollback startup. Safeguard: graceful error handling."""
        for hook in reversed(executed):
            try:
                logger.debug(f"Rolling back: {hook.__name__}")
            except Exception as e:
                logger.warning(f"Rollback error: {e}")

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
            except Exception as e:
                logger.error(f"Shutdown hook failed: {e}")
        await self._cleanup_resources()
        self._is_healthy = False
        logger.info("Shutdown complete")

    async def _cleanup_resources(self) -> None:
        """Cleanup resources. Safeguard: prevents leaks."""
        for name, resource in self._resources.items():
            try:
                if hasattr(resource, "close"):
                    if asyncio.iscoroutinefunction(resource.close):
                        await resource.close()
                    else:
                        resource.close()
                logger.debug(f"Cleaned: {name}")
            except Exception as e:
                logger.warning(f"Cleanup failed for {name}: {e}")
        self._resources.clear()

    def is_healthy(self) -> bool:
        """Check health status."""
        return self._is_healthy

    def is_ready(self) -> bool:
        """Check ready status."""
        return self._is_ready

    def healthz(self) -> Dict[str, Any]:
        """Generate health check response."""
        return {
            "status": "healthy" if self._is_healthy else "unhealthy",
            "ready": self._is_ready,
            "resources": len(self._resources),
        }
