"""
Facade Fastapi Module

This module provides functionality for facade fastapi.

Usage:
    from server.facade_fastapi import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

from fastapi import FastAPI

from mcp.middleware.rate_limit_middleware import RateLimitMiddleware
from mcp.observability.metrics import Timer, increment
from mcp.server.adapter_loader import lazy_connect_all
from mcp.server.jsonrpc_adapter import register_jsonrpc_routes
from mcp.server.middleware.auth import APIKeyAuthMiddleware
from mcp.server.routes_health import register_health_routes
from mcp.server.tracing import ensure_request_id, init_tracing

APP = FastAPI(title="MCP Façade (FastAPI)")
logger = logging.getLogger(__name__)

init_tracing(service_name="mcp-facade")

register_health_routes(APP)
register_jsonrpc_routes(APP)

APP.add_middleware(APIKeyAuthMiddleware)
APP.add_middleware(RateLimitMiddleware)


@APP.on_event("startup")
async def startup_event():
    ok = await lazy_connect_all(timeout=1.0)
    if not ok:
        logger.warning("Adapter connect failed during startup; continuing in degraded mode.")


@APP.middleware("http")
async def request_id_middleware(request, call_next):
    request_id = ensure_request_id(request)
    increment("requests_total")
    with Timer("request_latency"):
        response = await call_next(request)
    response.headers.setdefault("X-Request-Id", request_id)
    return response
