"""
Routes Health Module

This module provides functionality for routes health.

Usage:
    from server.routes_health import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .adapter_loader import load_adapter

logger = logging.getLogger(__name__)


def register_health_routes(app: FastAPI, adapter_loader_fn=load_adapter) -> None:
    @app.get("/health")
    async def health_root():
        adapter, adapter_path = adapter_loader_fn()
        try:
            adapter_status = adapter.health_check()
        except (IOError, OSError):
            logger.warning("Exception occurred", exc_info=True)
            adapter_status = {"status": "degraded"}
        payload = {
            "service": "mcp-facade",
            "status": "ok",
            "adapter": adapter_path,
            "adapter_status": adapter_status,
        }
        return JSONResponse(content=payload)

    @app.get("/mcp/v1/health")
    async def mcp_health():
        adapter, adapter_path = adapter_loader_fn()
        try:
            adapter_status = adapter.health_check()
        except (IOError, OSError):
            logger.warning("Exception occurred", exc_info=True)
            adapter_status = {"status": "degraded"}
        return JSONResponse(
            content={
                "status": "ok",
                "adapter": adapter_path,
                "adapter_status": adapter_status,
            }
        )
