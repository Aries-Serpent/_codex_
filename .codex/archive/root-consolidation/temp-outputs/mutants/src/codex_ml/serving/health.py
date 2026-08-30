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
    except ImportError:
        logger.debug("psutil unavailable; disk-space readiness check skipped")
        checks["disk_space"] = {"status": "skipped", "reason": "psutil not available"}
    except (IOError, OSError):
        logger.warning("Disk space readiness check failed")
        checks["disk_space"] = {"status": "error", "error": "disk_space_check_failed"}
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
        logger.warning("FastAPI is required for health endpoints")
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
        try:
            return readiness_check()
        except Exception:
            logger.warning("Readiness probe failed")
            return {
                "ready": False,
                "timestamp": time.time(),
                "checks": {"status": "error", "error": "readiness_check_failed"},
            }

    @router.get("/healthz")
    async def healthz() -> dict[str, Any]:
        """Kubernetes-style health check endpoint."""
        return health_check()

    @router.get("/readyz")
    async def readyz() -> dict[str, Any]:
        """Kubernetes-style readiness check endpoint."""
        try:
            return readiness_check()
        except Exception:
            logger.warning("Readiness probe failed")
            return {
                "ready": False,
                "timestamp": time.time(),
                "checks": {"status": "error", "error": "readiness_check_failed"},
            }

    return router
