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

from fastapi import FastAPI

import logging

from src.mcp.middleware.rate_limit_middleware import RateLimitMiddleware  # type: ignore
from src.mcp.observability.metrics import Timer, increment  # type: ignore
from src.mcp.server.adapter_loader import lazy_connect_all
from src.mcp.server.middleware.auth import APIKeyAuthMiddleware  # type: ignore
from src.mcp.server.routes_health import register_health_routes
from src.mcp.server.jsonrpc_adapter import register_jsonrpc_routes
from src.mcp.server.tracing import ensure_request_id, init_tracing  # type: ignore

APP = FastAPI(title="MCP Façade (FastAPI)")
logger = logging.getLogger(__name__)

init_tracing(service_name="mcp-facade")

register_health_routes(APP)
register_jsonrpc_routes(APP)

APP.add_middleware(APIKeyAuthMiddleware)
APP.add_middleware(RateLimitMiddleware)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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
