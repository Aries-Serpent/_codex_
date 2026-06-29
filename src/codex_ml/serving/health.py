"""Health and readiness check endpoints for deployment monitoring."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["get_health_router", "health_check", "readiness_check"]


def health_check() -> dict[str, Any]:
    """Basic health check - service is running and responsive.

    Returns:
        dict with status and timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "codex-ml",
    }


def readiness_check() -> dict[str, Any]:
    """Readiness check - service is ready to handle requests.

    Checks:
    - Disk space availability
    - Required directories exist
    - Environment variables set

    Returns:
        dict with ready status and check results.
    """
    checks = {}
    all_ready = True

    # Check disk space
    try:
        import psutil

        disk = psutil.disk_usage("/")
        disk_free_gb = disk.free / (1024**3)
        checks["disk_space"] = {
            "free_gb": round(disk_free_gb, 2),
            "percent_free": round(100 - disk.percent, 1),
            "status": "ok" if disk_free_gb > 1.0 else "warning",
        }
        if disk_free_gb < 1.0:
            all_ready = False
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        checks["disk_space"] = {"status": "skipped", "reason": "psutil not available"}
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        checks["disk_space"] = {"status": "error", "error": str(e)}
        all_ready = False

    # Check required directories
    required_dirs = [".codex", "src", "configs"]
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        exists = dir_path.exists()
        checks[f"dir_{dir_name}"] = {
            "exists": exists,
            "status": "ok" if exists else "missing",
        }
        if not exists:
            all_ready = False

    # Check environment
    env_vars = ["PYTHONPATH"]
    for var in env_vars:
        value = os.environ.get(var)
        checks[f"env_{var}"] = {
            "set": value is not None,
            "status": "ok" if value else "not_set",
        }

    return {
        "ready": all_ready,
        "timestamp": time.time(),
        "checks": checks,
    }


def get_health_router() -> None:
    """Get FastAPI router with health endpoints.

    Returns:
        FastAPI APIRouter with /health and /ready endpoints.

    Raises:
        ImportError: If FastAPI is not installed.
    """
    try:
        from fastapi import APIRouter
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        raise ImportError(
            "FastAPI is required for health endpoints. Install with: pip install fastapi"
        ) from e

    router = APIRouter(tags=["health"])

    @router.get("/health")
    async def health() -> dict[str, Any]:
        """Health check endpoint - always returns 200 if service is running."""
        return health_check()

    @router.get("/ready")
    async def readiness() -> dict[str, Any]:
        """Readiness check endpoint - returns 200 if service is ready."""
        return readiness_check()
        # Could return 503 if not ready, but for now return 200 with ready=false

    @router.get("/healthz")
    async def healthz() -> dict[str, Any]:
        """Kubernetes-style health check endpoint."""
        return health_check()

    @router.get("/readyz")
    async def readyz() -> dict[str, Any]:
        """Kubernetes-style readiness check endpoint."""
        return readiness_check()

    return router
